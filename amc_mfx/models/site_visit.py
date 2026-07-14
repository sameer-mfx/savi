from odoo import models, fields, api, _
from odoo.exceptions import UserError

class SiteVisit(models.Model):
    _name = 'amc.site.visit'
    _description = 'AMC Site Visit'
    _inherit = ['mail.thread', 'mail.activity.mixin']

    name = fields.Char(string='AMC Visit Reference', required=True, readonly=True, default='New', copy=False, tracking=True)
    display_name = fields.Char(compute='_compute_display_name', string='Display Name', store=True)
    engineer_ids = fields.Many2many(comodel_name='res.users', relation='amc_site_visit_engineer_rel', column1='visit_id', column2='user_id', string='Engineers', copy=False, tracking=True)
    performance_rating = fields.Selection(string='Performance Rating', selection=[(str(i), str(i)) for i in range(6)], default='0', tracking=True)
    assigned_by = fields.Many2one(comodel_name='res.users', string='Assigned By', copy=False)
    partner_id = fields.Many2one(comodel_name='res.partner', string='Customer', required=True)
    partner_address = fields.Char(string='Address')
    partner_email = fields.Char(string='Email', related='partner_id.email', readonly=True)
    partner_phone = fields.Char(string='Mobile', related='partner_id.mobile', readonly=True)
    date_order = fields.Datetime(string='Order Date', tracking=True)
    date_confirm = fields.Datetime(string='Confirm Date', tracking=True)
    amc_order_id = fields.Many2one(comodel_name='amc.order', required=True, ondelete='restrict')
    company_id = fields.Many2one(comodel_name='res.company', string='Company', required=True, default=lambda self: self.env.company, readonly=True)
    state = fields.Selection(selection=[('draft', 'Draft'), ('waiting', 'To Approve'), ('done', 'Approved'), ('cancel', 'Cancelled')], default='draft', copy=False, required=True, tracking=True)
    note = fields.Text(string="Remarks")
    visit_line_ids = fields.One2many(comodel_name='amc.site.visit.line', inverse_name='visit_id', string='AMC Visit Lines', required=True)
    replacement_ids = fields.One2many(comodel_name='amc.replacement', inverse_name='visit_id', string='Replacements')
    expense_ids = fields.One2many(comodel_name='amc.expense', inverse_name='visit_id', string='Expenses')
    replacement_count = fields.Integer(compute='_compute_rep_exp_counts')
    expense_count = fields.Integer(compute='_compute_rep_exp_counts')
    calendar_color = fields.Integer(string='Calendar Color', compute='_compute_calendar_color', store=True)
    satisfaction_email_sent = fields.Boolean(string='Satisfaction Survey Sent', readonly=True, copy=False)
    satisfaction_email_sent_date = fields.Datetime(string='Survey Sent On', readonly=True, copy=False)
    satisfaction_email_sent_by = fields.Many2one(comodel_name='res.users', string='Survey Sent By', readonly=True, copy=False)

    def action_send_satisfaction_email(self):
        self.ensure_one()
        template = self.env.ref('amc_mfx.email_template_amc_visit_satisfaction', raise_if_not_found=False)
        if not template:
            raise UserError(_("Satisfaction email template is not configured."))
        if not self.partner_id or not self.partner_id.email:
            raise UserError(_("The customer does not have an email address configured."))
        return {
            'type': 'ir.actions.act_window',
            'name': _('Resend Satisfaction Survey') if self.satisfaction_email_sent else _('Send Satisfaction Survey'),
            'res_model': 'mail.compose.message',
            'view_mode': 'form',
            'target': 'new',
            'context': {
                'default_model': 'amc.site.visit',
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

    def _compute_rep_exp_counts(self):
        for rec in self:
            rec.replacement_count = len(rec.replacement_ids)
            rec.expense_count = len(rec.expense_ids)

    def action_submit_replacements(self):
        self.ensure_one()
        drafts = self.replacement_ids.filtered(lambda r: r.state == 'draft')
        if not drafts:
            raise UserError(_("There are no draft replacements to submit."))
        drafts.action_submit()

    def action_submit_expenses(self):
        self.ensure_one()
        drafts = self.expense_ids.filtered(lambda e: e.state == 'draft')
        if not drafts:
            raise UserError(_("There are no draft expenses to submit."))
        drafts.action_submit()

    @api.depends('name', 'engineer_ids')
    def _compute_display_name(self):
        for record in self:
            if record.name and record.engineer_ids:
                engineers = ', '.join(record.engineer_ids.mapped('name'))
                record.display_name = f"{record.name} - {engineers}"
            else:
                record.display_name = record.name or ''

    @api.depends('date_order')
    def _compute_calendar_color(self):
        today = fields.Date.context_today(self)
        for record in self:
            if record.date_order:
                date_order_date = fields.Date.to_date(record.date_order)
                if date_order_date < today:
                    record.calendar_color = 1  # Red
                elif date_order_date == today:
                    record.calendar_color = 10  # Green
                else:
                    record.calendar_color = 0  # Default/other

    def amc_button_approve(self):
        if self.state == 'draft':
            self.write({'state': 'done', 'date_confirm': fields.datetime.now()})

    def amc_button_cancel(self):
        if self.state == 'draft':
            self.write({'state': 'cancel'})
        else:
            raise UserError(_("This Visit %s cannot be cancelled" %self.name))

    @api.model_create_multi
    def create(self, vals_list):
        for vals in vals_list:
            if not vals.get('name') or vals['name'] == 'New':
                vals['name'] = self.env['ir.sequence'].next_by_code('amc.site.visit') or _('New')
        records = super().create(vals_list)
        for rec in records:
            if rec.amc_order_id and rec.amc_order_id.state != 'approved':
                raise UserError(_(
                    "Site visits can only be created once AMC Order '%s' is approved. Current status: %s."
                ) % (rec.amc_order_id.name, dict(rec.amc_order_id._fields['state'].selection).get(rec.amc_order_id.state, rec.amc_order_id.state)))
        return records

    def copy(self, default=None):
        raise UserError(_("Duplication of AMC Site Visits is not allowed."))

    def unlink(self):
        for visit in self:
            if visit.state != 'draft':
                raise UserError(_("You are not allowed to delete this Visit %s" % visit.name))
        return super().unlink()

class SiteVisitLine(models.Model):
    _name = "amc.site.visit.line"
    _description = "Site Visit Line"
    _rec_name = "description"

    product_id = fields.Many2one(comodel_name='product.product', string='Product')
    service_id = fields.Many2one(comodel_name='amc.services', string='Service Name')
    description = fields.Char(string='Service Description')
    product_identification_ids = fields.Many2many(comodel_name='stock.lot', string='Identification Numbers', copy=False)
    location = fields.Char(string='Location')
    company_id = fields.Many2one(comodel_name='res.company', string='Company', required=True, default=lambda self: self.env.company)
    amc_order_line_id = fields.Many2one('amc.order.lines')
    visit_id = fields.Many2one(comodel_name='amc.site.visit', ondelete='cascade')
    state = fields.Selection(related='visit_id.state', store=True)

class Amc(models.Model):
    _inherit = 'amc.order'

    amc_site_visit_ids = fields.Many2many(comodel_name='amc.site.visit', relation='amc_order_amc_site_visit_rel', column_1='amc_order_id', column_2='visit_id', copy=False)
    amc_visit_count = fields.Integer(compute="_compute_amc_visit_count", copy=False)
    # Kept for backward compatibility (previously used before wizard was introduced)
    assigned_to = fields.Many2one(comodel_name='res.users', string='Assigned To', copy=False)
    visit_date = fields.Datetime(string='Visit Date', copy=False)

    def create_site_visit(self):
        if self.is_amc_expired:
            raise UserError(_("You are not allowed to create visit for expired AMC Order"))
        return {
            'type': 'ir.actions.act_window',
            'name': _('Create AMC Visit'),
            'res_model': 'amc.visit.wizard',
            'view_mode': 'form',
            'target': 'new',
            'context': {'active_id': self.id, 'active_model': 'amc.order'},
        }

    def button_show_amc_visits(self):
        action = self.env.ref('amc_mfx.action_amc_visit_list').read()[0]
        amc_visits = self.mapped('amc_site_visit_ids')
        if len(amc_visits) > 1:
            action['domain'] = [('id', 'in', amc_visits.ids)]
        elif amc_visits:
            action['views'] = [(self.env.ref('amc_mfx.amc_visit_form_view').id, 'form')]
            action['res_id'] = amc_visits.id
        return action

    def _compute_amc_visit_count(self):
        for rec in self:
            rec.amc_visit_count = len(rec.amc_site_visit_ids)