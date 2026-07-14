from odoo import models, fields, api, _
from dateutil.relativedelta import relativedelta
from datetime import timedelta

class SaleOrder(models.Model):
    _inherit = 'sale.order'

    tandc_id = fields.Many2one(comodel_name='def.tandc', string="Terms & Conditions")
    email = fields.Char(string='Email')
    mobile = fields.Char(string='Mobile')
    purchase_order_ids = fields.Many2many(comodel_name='purchase.order', string='Purchase Orders')
    reminder_count = fields.Integer(string='Reminder Count')
    remind_every = fields.Integer(string='Remind Every (Days)')
    last_reminder_date = fields.Date(string='Last Reminder Date')
    next_reminder_date = fields.Date(string='Next Reminder Date', compute='_compute_next_reminder_date', store=True)
    quotation_sent_date = fields.Date(string='Quotation Sent Date')

    @api.onchange('state')
    def _onchange_state(self):
        if self.state == 'sent':
            self.quotation_sent_date = fields.Date.today()

    @api.depends('last_reminder_date', 'remind_every', 'validity_date')
    def _compute_next_reminder_date(self):
        today = fields.Date.today()
        for rec in self:
            if rec.validity_date and rec.validity_date >= today and rec.last_reminder_date and rec.remind_every:
                rec.next_reminder_date = rec.last_reminder_date + timedelta(days=rec.remind_every)
            else:
                rec.next_reminder_date = False

    def send_reminder(self):
        template = self.env.ref('custom_crm_mfx.email_template_sale_quotation_reminder')
        ctx = {
            'default_model': 'sale.order',
            'default_res_ids': self.ids,
            'default_use_template': bool(template),
            'default_template_id': template.id,
            'default_composition_mode': 'comment',  # or 'mass_mail' / 'reply' depending on the case
        }

        return {
            'type': 'ir.actions.act_window',
            'view_mode': 'form',
            'res_model': 'mail.compose.message',
            'target': 'new',
            'context': ctx,
        }

    @api.model
    def send_sale_reminder_emails(self):
        today = fields.Date.today()
        template = self.env.ref('custom_crm_mfx.email_template_sale_quotation_reminder')

        orders = self.search([('state', '=', 'sent'), ('quotation_sent_date', '!=', False), ('validity_date', '>=', today), ('remind_every', '>', 0), '|', ('last_reminder_date', '=', False), ('next_reminder_date', '<=', today)])

        for order in orders:
            template.send_mail(order.id, force_send=True)
            order.last_reminder_date = today
            order.reminder_count += 1

    def action_send_custom_quotation_email(self):
        """Open email composer using the dedicated quotation template and report."""
        self.ensure_one()
        self.order_line._validate_analytic_distribution()
        lang = self.env.context.get('lang')
        template = self.env.ref(
            'custom_crm_mfx.mail_template_sale_quotation_any_state',
            raise_if_not_found=False,
        )
        if template and template.lang:
            lang = template._render_lang(self.ids)[self.id]
        ctx = {
            'default_model': 'sale.order',
            'default_res_ids': self.ids,
            'default_template_id': template.id if template else None,
            'default_use_template': bool(template),
            'default_composition_mode': 'comment',
            'default_email_layout_xmlid': 'mail.mail_notification_layout_with_responsible_signature',
            'mark_so_as_sent': self.state in ('draft', 'sent'),
            'force_email': True,
            'model_description': self.with_context(lang=lang).type_name,
        }
        return {
            'type': 'ir.actions.act_window',
            'view_mode': 'form',
            'res_model': 'mail.compose.message',
            'views': [(False, 'form')],
            'view_id': False,
            'target': 'new',
            'context': ctx,
        }

    @api.onchange('partner_id')
    def fill_email_and_mobile_in_so(self):
        for rec in self:
            rec.email = rec.partner_id.email
            rec.mobile = rec.partner_id.mobile

    @api.constrains('mobile', 'email')
    def fill_email_and_mobile_in_partner(self):
        for rec in self:
            if rec.email:
                rec.partner_id.email = rec.email
            if rec.mobile:
                rec.partner_id.mobile = rec.mobile

    @api.onchange('tandc_id')
    def fill_terms_and_conditions_in_so(self):
        for rec in self:
            if rec.tandc_id:
                rec.note = rec.tandc_id.terms_and_conditions
            else:
                rec.note = ''

    def action_confirm(self):
        for rec in self:
            for line in rec.order_line:
                if line.product_id and line.warranty_interval and line.warranty_unit:
                    line.warranty_start_date = fields.Date.today()
                    if line.warranty_unit == 'month':
                        line.warranty_end_date = line.warranty_start_date + relativedelta(months=line.warranty_interval) - timedelta(days=1)
                    elif line.warranty_unit == 'year':
                        line.warranty_end_date = line.warranty_start_date + relativedelta(years=line.warranty_interval) - timedelta(days=1)
        res = super(SaleOrder, self).action_confirm()
        self._create_po_activities()
        return res

    def _get_po_activity_users(self, order):
        """Return admin users and the order salesperson for PO follow-up."""
        admin_group = self.env.ref('base.group_system', raise_if_not_found=False)
        users = admin_group.sudo().users if admin_group else self.env['res.users'].sudo()
        if order.user_id:
            users |= order.user_id.sudo()
        user_ids = users.filtered(lambda user: user.active and not user.share).ids
        return self.env['res.users'].browse(user_ids)

    def _create_po_activities(self):
        """Create PO follow-up activities for admins and the SO salesperson."""
        for order in self:
            activity_users = self._get_po_activity_users(order)
            if not activity_users:
                continue
            products = order.order_line.filtered(lambda l: l.product_id).mapped('product_id')
            if not products:
                continue
            product_list = ', '.join(products.mapped('name'))
            note = _(
                "Sales Order <b>%s</b> has been confirmed. "
                "Please create a Purchase Order for the following products:<br/><b>%s</b>",
                order.name, product_list,
            )
            for user in activity_users:
                order.activity_schedule(
                    act_type_xmlid='mail.mail_activity_data_todo',
                    summary=_("Create PO for %s", order.name),
                    note=note,
                    user_id=user.id,
                    date_deadline=fields.Date.today() + timedelta(days=1),
                )

class DefTandC(models.Model):
    _name = 'def.tandc'

    name = fields.Char(required=True)
    terms_and_conditions = fields.Html(required=True)
    type = fields.Selection(selection=[('sale', 'Sale'), ('purchase', 'Purchase')], readonly=True, force_save=True)

    @api.model
    def create(self, vals):
        if self.env.context.get('from_sales'):
            vals['type'] = 'sale'
        elif self.env.context.get('from_purchase'):
            vals['type'] = 'purchase'
        return super(DefTandC, self).create(vals)

class SaleOrderLine(models.Model):
    _inherit = 'sale.order.line'

    warranty_start_date = fields.Date(string='Warranty Start Date', copy=False)
    warranty_interval = fields.Integer(string='Warranty Interval', copy=False)
    warranty_unit = fields.Selection([('month', 'Months'), ('year', 'Years')], string='Warranty Unit', copy=False)
    warranty_end_date = fields.Date(string='Warranty End Date', copy=False)

    @api.depends('product_id', 'product_uom', 'product_uom_qty')
    def _compute_price_unit(self):
        for line in self:
            # check if there is already invoiced amount. if so, the price shouldn't change as it might have been
            # manually edited
            if line.qty_invoiced > 0 or (line.product_id.expense_policy == 'cost' and line.is_expense):
                continue
            if not line.product_uom or not line.product_id:
                line.price_unit = 0.0
            else:
                if not line.price_unit:
                    line = line.with_company(line.company_id)
                    price = line._get_display_price()
                    line.price_unit = line.product_id._get_tax_included_unit_price_from_price(
                        price,
                        line.currency_id or line.order_id.currency_id,
                        product_taxes=line.product_id.taxes_id.filtered(
                            lambda tax: tax.company_id == line.env.company
                        ),
                        fiscal_position=line.order_id.fiscal_position_id,
                    )