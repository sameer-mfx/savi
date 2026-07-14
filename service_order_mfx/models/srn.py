from odoo import models, fields, api, _
from odoo.exceptions import UserError
from datetime import datetime
from dateutil.relativedelta import relativedelta

class Srn(models.Model):
    _name = 'srn'
    _description = 'SRN'
    _rec_name = 'display_name'
    _order = "id desc"
    _inherit = ['mail.thread', 'mail.activity.mixin', 'portal.mixin']

    name = fields.Text(string='Srn Reference', required=True)
    display_name = fields.Char(compute='_compute_display_name', string='Display Name')
    user_id = fields.Many2one(comodel_name='res.users', string='Responsible', copy=False, default=lambda self: self.env.user)
    performance_rating = fields.Selection(string='Performance Rating', selection=[('0', '0'), ('1', '1'), ('2', '2'), ('3', '3'), ('4', '4'), ('5', '5')], default='0')
    assigned_by = fields.Many2one(comodel_name='res.users', string='Assigned By', copy=False)
    customer_id = fields.Many2one(comodel_name='res.partner', string='Customer', required=True)
    customer_ref = fields.Text('Customer Reference')
    date_order = fields.Datetime(string='Order Date')
    date_confirm = fields.Datetime('Confirm Date')
    deadline = fields.Datetime('Deadline')
    service_order_ids = fields.Many2many(comodel_name='service.order', required=True)
    company_id = fields.Many2one(comodel_name='res.company', string='Company', required=True, default=lambda self: self.env.user.company_id.id)
    state = fields.Selection(selection=[('draft', 'Draft'), ('waiting', 'To Approve'), ('done', 'Approved'), ('cancel', 'Cancelled')], default='draft', copy=False, required=True)
    note = fields.Text("Remarks")
    srn_line_ids = fields.One2many(comodel_name='srn.line', inverse_name='srn_id', string='Srn Lines', required=True)
    calendar_color = fields.Integer(string='Calendar Color', compute='_compute_calendar_color', store=True)
    satisfaction_email_sent = fields.Boolean(string='Satisfaction Survey Sent', readonly=True, copy=False)
    satisfaction_email_sent_date = fields.Datetime(string='Survey Sent On', readonly=True, copy=False)
    satisfaction_email_sent_by = fields.Many2one(comodel_name='res.users', string='Survey Sent By', readonly=True, copy=False)

    def action_send_satisfaction_email(self):
        self.ensure_one()
        template = self.env.ref('service_order_mfx.email_template_srn_satisfaction', raise_if_not_found=False)
        if not template:
            raise UserError(_("Satisfaction email template is not configured."))
        if not self.customer_id or not self.customer_id.email:
            raise UserError(_("The customer does not have an email address configured."))
        return {
            'type': 'ir.actions.act_window',
            'name': _('Resend Satisfaction Survey') if self.satisfaction_email_sent else _('Send Satisfaction Survey'),
            'res_model': 'mail.compose.message',
            'view_mode': 'form',
            'target': 'new',
            'context': {
                'default_model': 'srn',
                'default_res_ids': self.ids,
                'default_template_id': template.id,
                'default_composition_mode': 'comment',
                'default_email_layout_xmlid': 'mail.mail_notification_light',
                'mark_satisfaction_sent': True,
            },
        }

    def message_post(self, **kwargs):
        message = super().message_post(**kwargs)
        if self.env.context.get('mark_satisfaction_sent') and message and message.message_type == 'comment':
            self.sudo().write({
                'satisfaction_email_sent': True,
                'satisfaction_email_sent_date': fields.Datetime.now(),
                'satisfaction_email_sent_by': self.env.user.id,
            })
        return message

    @api.depends('name', 'user_id')
    def _compute_display_name(self):
        for record in self:
            if record.name and record.user_id:
                record.display_name = record.name + ' - ' + record.user_id.name

    @api.depends('date_order')
    def _compute_calendar_color(self):
        today = fields.Date.today()
        for record in self:
            if record.date_order:
                if record.date_order.date() < today:
                    record.calendar_color = 1  # Red
                elif record.date_order.date() == today:
                    record.calendar_color = 10  # Green

    def srn_button_approve(self):
        if self.state == 'draft':
            self.write({'state': 'done', 'date_confirm': datetime.now()})

    def srn_button_cancel(self):
        if self.state == 'draft':
            self.write({'state': 'cancel'})
        else:
            raise UserError(_("This SRN %s cannot be cancelled" %self.name))

    @api.model
    def create(self, vals):
        vals['name'] = self.env['ir.sequence'].next_by_code('srn') or _('New')
        res = super(Srn, self).create(vals)
        return res

    def copy(self, default=None):
        # Raise an error to prevent duplication
        raise UserError("Duplication of SRN records is not allowed.")

    def unlink(self):
        for srn in self:
            if srn.state != 'draft':
                raise UserError(_("You are not allowed to delete this SRN %s" % srn.name))
        return super(Srn, self).unlink()

class SrnLine(models.Model):
    _name = "srn.line"
    _description = "Srn Line"
    _rec_name = "description"

    # **============== Fields ==============**

    product_id = fields.Many2one(comodel_name='product.product', string='Product')
    service_product_id = fields.Many2one(comodel_name='product.product', domain="[('detailed_type', '=', 'service')]", required=True)
    description = fields.Char('Description')
    product_qty = fields.Float(string="Qty", required=True)
    product_identification_ids = fields.Many2many(comodel_name='stock.lot', string='Identification Numbers', copy=False)
    price = fields.Float(string='Price Unit')
    tax_ids = fields.Many2many('account.tax')
    company_id = fields.Many2one(comodel_name='res.company', string='Company', required=True, default=lambda self: self.env.user.company_id.id)
    service_order_line_id = fields.Many2one(comodel_name='service.order.line')
    srn_id = fields.Many2one(comodel_name='srn', ondelete='cascade')
    state = fields.Selection(related='srn_id.state', store=True, required=True)

class ServiceOrder(models.Model):
    _inherit = 'service.order'

    # **============== Fields ==============**

    srn_ids = fields.Many2many(comodel_name='srn', relation='so_srn_rel', column1='service_order_id', column2='srn_id', copy=False)
    srn_count = fields.Integer(compute="_compute_srn_count", copy=False)

    # **============== Methods ==============**

    def test_crn(self):
        self._cron_create_srn_for_recurring_service_orders()

    def _cron_create_srn_for_recurring_service_orders(self):
        today = fields.Date.today()
        recurring_sso = self.search([('is_amc', '=', True),('state', '=', 'approved')]).filtered(lambda s: s.amc_start_date == today and (s.repeat_type == 'forever' or (s.repeat_type == 'until' and s.repeat_until >= today)))
        non_recurring_approved_sso = self.search([('is_amc', '=', False), ('state', '=', 'approved'), ('srn_ids', '=', False)])
        for sso in recurring_sso:
            last_srn_date = sso.srn_ids.filtered(lambda s: s.id and s.state != 'cancel').sorted(key=lambda s: s.id, reverse=True)[0].date_order.date() if sso.srn_ids else False
            if not last_srn_date:
                sso.sso_create_srn()
            else:
                if sso.repeat_unit == 'month':
                    next_srn_date = last_srn_date + relativedelta(months=sso.repeat_interval)
                elif sso.repeat_unit == 'year':
                    next_srn_date = last_srn_date + relativedelta(years=sso.repeat_interval)
                if next_srn_date == today:
                    sso.sso_create_srn()

        for sso in non_recurring_approved_sso:
            sso.sso_create_srn()

    def sso_create_srn(self):
        srn_lines = self.env['srn.line']
        for line in self.order_line_ids:
            vals = {
                'product_id': line.product_id.id,
                'service_product_id': line.service_product_id.id,
                'description': line.product_id.name,
                'product_qty': line.quantity,
                'product_identification_ids': line.product_identification_ids.ids,
                'price': line.unit_price if not line.under_warranty else 0,
                'tax_ids': line.tax_ids.ids,
                'service_order_line_id': line.id,
                'state': 'draft'
            }
            srn_lines += self.env['srn.line'].create(vals)
        if srn_lines:
            srn_vals = {
                'assigned_by': self.user_id.id,
                'user_id': self.assigned_to.id,
                'customer_id': self.customer_id.id,
                'customer_ref': self.customer_ref,
                'date_order': fields.datetime.now() if not self.is_amc else self.visit_date,
                'company_id': self.company_id.id,
                'service_order_ids': [(4, self.id)]
            }
            srn = self.env['srn'].create(srn_vals)
            srn_lines.srn_id = srn.id
            self.srn_ids += srn

    def spo_button_show_srns(self):
        action = self.env.ref('service_order_mfx.action_srn_list').read()[0]
        srn = self.mapped('srn_ids')
        if len(srn) > 1:
            action['domain'] = [('id', 'in', srn.ids)]
        elif srn:
            action['views'] = [
                (self.env.ref('service_order_mfx.srn_form_view').id, 'form')]
            action['res_id'] = srn.id
        return action

    def _compute_srn_count(self):
        self.srn_count = len(self.srn_ids)