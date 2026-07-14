from odoo import models, fields, api, _
from odoo.exceptions import UserError

class ServiceOrder(models.Model):
    _name = 'service.order'
    _inherit = ['mail.thread', 'mail.activity.mixin']
    _description = 'Service Order'

    name = fields.Char(string='Service Order', required=True, readonly=True, copy=False, default=lambda self: _('New'))
    user_id = fields.Many2one(comodel_name='res.users', string='Responsible', default=lambda self: self.env.user)
    assigned_to = fields.Many2one(comodel_name='res.users', string='Assigned To', copy=False)
    customer_id = fields.Many2one(comodel_name='res.partner', string='Customer')
    customer_ref = fields.Char(string='Customer Reference')
    visit_date = fields.Datetime(string='Visit Date', copy=False)
    currency_id = fields.Many2one('res.currency', 'Currency', required=True, default=lambda self: self.env.user.company_id.currency_id.id)
    date_order = fields.Datetime(string='Order Date', default=fields.Datetime.now, copy=False)
    date_approve = fields.Datetime(string='Confirmed Date', copy=False)
    company_id = fields.Many2one('res.company', 'Company', required=True, default=lambda self: self.env.user.company_id.id)
    is_amc = fields.Boolean(string='Is AMC')
    amc_start_date = fields.Date(string='AMC Start Date')
    repeat_interval = fields.Integer(string='Repeat Interval', default=1)
    repeat_unit = fields.Selection(selection=[('month', 'Month'), ('year', 'Year')], string='Repeat Type')
    repeat_type = fields.Selection(selection=[('forever', 'Forever'), ('until', 'Until')], string='Repeat Type')
    repeat_until = fields.Date(string='Repeat Until')
    order_line_ids = fields.One2many(comodel_name='service.order.line', inverse_name='order_id', string='Order Lines', copy=True)
    state = fields.Selection(selection=[('draft', 'Draft'), ('to_approve', 'To Approve'), ('approved', 'Approved'), ('cancel', 'Cancelled')], string='Status', required=True, copy=False, default='draft', tracking=True)
    notes = fields.Text('Notes')
    terms_and_conditions = fields.Text('Terms and Conditions')

    @api.constrains('amc_start_date', 'repeat_type', 'repeat_until')
    def _sso_date_constrains(self):
        if self.repeat_until and self.repeat_type == 'until' and self.repeat_until < self.amc_start_date:
            raise UserError(_("Repeat Until date must be greater than or equal to AMC Start Date"))
        if self.amc_start_date and self.amc_start_date < fields.Date.today():
            raise UserError(_("AMC Start Date must be greater than or equal to today"))

    @api.constrains('visit_date')
    def _update_srn_date(self):
        draft_srns = self.srn_ids.filtered(lambda s: s.state == 'draft')
        if self.visit_date and draft_srns:
            draft_srns.sorted(key=lambda s: s.id, reverse=True)[0].date_order = self.visit_date

    def sso_check_product_and_partner_status(self):
        for order in self:
            if not order.customer_id.active:
                raise UserError(_("The partner %s is archived." %order.customer_id.display_name))
            inactive_products_in_lines = order.order_line_ids.mapped('product_id').filtered(lambda p: not p.active)
            if inactive_products_in_lines:
                raise UserError(_("The product(s) %s in %s are not active or archived." % ((', '.join(inactive_products_in_lines.mapped('name'))), order.name)))
            inactive_service_products_in_lines = order.order_line_ids.mapped('service_product_id').filtered(lambda p: not p.active)
            if inactive_service_products_in_lines:
                raise UserError(_("The service product(s) %s in %s are not active or archived." % ((', '.join(inactive_products_in_lines.mapped('name'))), order.name)))

    def sso_line_validations(self):
        for order in self:
            if not order.order_line_ids:
                raise UserError(_("Please add Service lines in %s." % order.name))
            seen_combinations = set()
            duplicate_lines = []
            for line in order.order_line_ids:
                length_of_product_identifications = len(line.product_identification_ids)
                if (line.quantity != length_of_product_identifications) and (line.is_tracked):
                    raise UserError(_("Quantity in line with product %s is %s and number of Product Identifications is %s in %s" %(line.product_id.name, line.quantity, length_of_product_identifications, order.name)))
                combination = (line.product_id.id, line.service_product_id.id)
                if combination in seen_combinations:
                    duplicate_lines.append(line)
                else:
                    seen_combinations.add(combination)
            if duplicate_lines:
                duplicate_messages = []
                for line in duplicate_lines:
                    product_name = line.product_id.name or 'Unknown Product'
                    service_product_name = line.service_product_id.name or 'Unknown Service Product'
                    duplicate_messages.append(_("Product %s and Service Product %s") % (product_name, service_product_name))
                raise UserError(_("Please remove duplicate lines with %s from AMC Order lines in %s." % (' '.join(duplicate_messages), order.name)))

    def sso_amc_approve(self):
        for order in self:
            if not order.order_line_ids:
                raise UserError(_("Please add lines in order %s" %order.name))
            for line in order.order_line_ids:
                if not order.is_amc and not line.quantity:
                    raise UserError(_("Quantity in line with product %s must be greater than zero for Non Recurring order %s" %(line.product_id.name, order.name)))

    def sso_action_approve(self):
        for order in self:
            order.sso_check_product_and_partner_status()
            if order.state == 'draft':
                order.sso_line_validations()
                name = self.env['ir.sequence'].next_by_code('service.order') or _('New')
                order.sso_amc_approve()
                order.write({'state': 'to_approve', 'name': name, 'date_order': fields.datetime.now()})
            else:
                raise UserError(_("The order %s is already confirmed" %order.name))

    def sso_action_confirm(self):
        for order in self:
            if order.state == 'to_approve':
                order.sso_check_product_and_partner_status()
                order.sso_line_validations()
                order.write({'state': 'approved', 'date_approve': fields.datetime.now()})
                if not order.is_amc or (order.is_amc and order.amc_start_date <= fields.date.today()):
                    order.sso_create_srn()
            else:
                raise UserError(_("This order %s is already approved" % order.name))

    def sso_action_cancel(self):
        for order in self:
            if order.state in ('draft', 'to_approve'):
                order.write({'state': 'cancel'})
            elif order.state != 'cancel':
                raise UserError(_("This order cannot be cancelled as it is approved"))

    def sso_action_draft(self):
        for order in self:
            if order.srn_ids.filtered(lambda s: s.state != 'draft'):
                raise UserError(_("You are not allowed to move this order %s to Draft state" %order.name))
            else:
                order.write({'state': 'draft'})
                order.srn_ids.state = 'cancel'
                order.srn_ids = False

    @api.model
    def create(self, vals):
        vals['name'] = self.env['ir.sequence'].next_by_code('service.quotation') or _('New')
        return super(ServiceOrder, self).create(vals)