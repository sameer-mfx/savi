from odoo import models, fields, api, _
from odoo.exceptions import UserError, ValidationError
from dateutil.relativedelta import relativedelta

class Amc(models.Model):
    _name = 'amc.order'
    _description = 'AMC'
    _order = 'name desc'
    _inherit = ['mail.thread', 'mail.activity.mixin']

    name = fields.Char(string='Service Order', required=True, readonly=True, copy=False, default=lambda self: _('New'))
    user_id = fields.Many2one(comodel_name='res.users', string='Responsible', copy=False, default=lambda self: self.env.user)
    partner_id = fields.Many2one(comodel_name='res.partner', string='Customer')
    partner_address = fields.Char(string='Address', related='partner_id.contact_address_inline')
    partner_email = fields.Char(string='Email', related='partner_id.email')
    partner_phone = fields.Char(string='Mobile', related='partner_id.mobile')
    company_id = fields.Many2one(comodel_name='res.company', string='Company', default=lambda self: self.env.user.company_id.id)
    currency_id = fields.Many2one(comodel_name='res.currency', string='Currency', required=True, default=lambda self: self.env.user.company_id.currency_id.id)
    amc_start_date = fields.Date(string='AMC Start Date', default=lambda self: fields.Date.context_today(self))
    amc_duration = fields.Integer(string='AMC Duration', default=1)
    amc_duration_unit = fields.Selection(selection=[('month', 'Month'), ('year', 'Year')], string='Duration Type')
    amc_end_date = fields.Date(string='AMC End Date', tracking=True)
    billing_cycle = fields.Selection(
        selection=[
            ('one_time', 'One-Time (Upfront)'),
            ('quarterly', 'Quarterly'),
            ('half_yearly', 'Half-Yearly'),
            ('annual', 'Annual'),
        ],
        string='Billing Cycle',
        tracking=True,
    )
    next_billing_date = fields.Date(string='Next Billing Date', compute='_compute_next_billing_date', store=True)
    is_amc_expired = fields.Boolean(string='Expired', compute='_compute_amc_validity')
    is_locked = fields.Boolean(string='Locked', default=False, copy=False, tracking=True)
    state = fields.Selection(selection=[('draft', 'Draft'), ('to_approve', 'To Approve'), ('approved', 'Approved'), ('cancel', 'Cancelled'), ('expired', 'Expired')], string='Status', default='draft', tracking=True)
    amc_lines_ids = fields.One2many(comodel_name='amc.order.lines', inverse_name='amc_id', string='AMC Order Lines', copy=True)
    notes = fields.Html('Notes')
    terms_and_conditions = fields.Html('Terms and Conditions')
    amount_untaxed = fields.Monetary(string="Untaxed Amount", store=True, compute='_compute_amounts', tracking=5)
    amount_tax = fields.Monetary(string="Taxes", store=True, compute='_compute_amounts')
    amount_total = fields.Monetary(string="Total", store=True, compute='_compute_amounts', tracking=4)
    tax_totals = fields.Binary(compute='_compute_tax_totals', exportable=False)

    @api.depends('amc_lines_ids.subtotal_price', 'amc_lines_ids.price_tax', 'amc_lines_ids.total_price')
    def _compute_amounts(self):
        """Compute the total amounts of the SO."""
        for order in self:
            order = order.with_company(order.company_id)
            order_lines = order.amc_lines_ids

            if order.company_id.tax_calculation_rounding_method == 'round_globally':
                tax_results = order.env['account.tax']._compute_taxes([
                    line._convert_to_tax_base_line_dict()
                    for line in order_lines
                ])
                totals = tax_results['totals']
                amount_untaxed = totals.get(order.currency_id, {}).get('amount_untaxed', 0.0)
                amount_tax = totals.get(order.currency_id, {}).get('amount_tax', 0.0)
            else:
                amount_untaxed = sum(order_lines.mapped('subtotal_price'))
                amount_tax = sum(order_lines.mapped('price_tax'))

            order.amount_untaxed = amount_untaxed
            order.amount_tax = amount_tax
            order.amount_total = order.amount_untaxed + order.amount_tax

    @api.depends_context('lang')
    @api.depends('amc_lines_ids.tax_ids', 'amc_lines_ids.unit_price', 'amount_total', 'amount_untaxed', 'currency_id')
    def _compute_tax_totals(self):
        for order in self:
            order = order.with_company(order.company_id)
            order_lines = order.amc_lines_ids
            order.tax_totals = order.env['account.tax']._prepare_tax_totals(
                [x._convert_to_tax_base_line_dict() for x in order_lines],
                order.currency_id or order.company_id.currency_id,
            )

    def _compute_amc_validity(self):
        """Compute whether AMC is expired (read-only flag for UI display)."""
        today = fields.Date.today()
        for rec in self:
            rec.is_amc_expired = bool(
                rec.amc_end_date and rec.amc_end_date < today and rec.state == 'approved'
            )

    def _cron_update_amc_validity(self):
        """Cron job: find approved AMCs past their end date and mark them expired."""
        today = fields.Date.today()
        expired_orders = self.search([
            ('state', '=', 'approved'),
            ('amc_end_date', '<', today),
            ('amc_end_date', '!=', False),
        ])
        if expired_orders:
            expired_orders.write({'state': 'expired'})

    @api.depends('amc_start_date', 'amc_end_date', 'billing_cycle', 'state')
    def _compute_next_billing_date(self):
        today = fields.Date.today()
        cycle_months = {
            'quarterly': 3,
            'half_yearly': 6,
            'annual': 12,
        }
        for rec in self:
            if not rec.amc_start_date or not rec.billing_cycle or rec.billing_cycle == 'one_time' or rec.state in ('cancel', 'expired', 'draft'):
                rec.next_billing_date = False
                continue
            months = cycle_months.get(rec.billing_cycle, 0)
            if not months:
                rec.next_billing_date = False
                continue
            # Walk forward from start date in billing cycle increments
            billing_date = rec.amc_start_date
            while billing_date <= today:
                billing_date = billing_date + relativedelta(months=months)
            # If next billing date exceeds AMC end date, no more billing
            if rec.amc_end_date and billing_date > rec.amc_end_date:
                rec.next_billing_date = False
            else:
                rec.next_billing_date = billing_date

    def _cron_billing_reminders(self):
        """Cron job: schedule activities for AMC orders with upcoming billing dates."""
        today = fields.Date.today()
        reminder_date = today + relativedelta(days=7)
        orders = self.search([
            ('next_billing_date', '>=', today),
            ('next_billing_date', '<=', reminder_date),
            ('state', '=', 'approved'),
        ])
        activity_type = self.env.ref('mail.mail_activity_data_todo', raise_if_not_found=False)
        for order in orders:
            # Check if an activity already exists for this billing date
            existing = self.env['mail.activity'].search([
                ('res_model', '=', 'amc.order'),
                ('res_id', '=', order.id),
                ('summary', 'like', 'Billing Follow-up'),
                ('date_deadline', '=', order.next_billing_date),
            ], limit=1)
            if not existing:
                order.activity_schedule(
                    'mail.mail_activity_data_todo',
                    date_deadline=order.next_billing_date,
                    summary=_("Billing Follow-up: %s") % order.partner_id.name,
                    note=_("Next billing date for AMC %s (%s billing) is %s. Please follow up with the customer regarding payment.") % (
                        order.name,
                        dict(order._fields['billing_cycle'].selection).get(order.billing_cycle, ''),
                        order.next_billing_date,
                    ),
                    user_id=order.user_id.id or self.env.user.id,
                )

    @api.onchange('amc_start_date', 'amc_duration', 'amc_duration_unit')
    def _onchange_amc_dates(self):
        today = fields.Date.today()
        if self.amc_start_date and self.amc_duration and self.amc_duration_unit:
            start_date = fields.Date.from_string(self.amc_start_date)
            if self.amc_duration_unit == 'year':
                end_date = start_date + relativedelta(years=self.amc_duration) - relativedelta(days=1)
            else:
                end_date = start_date + relativedelta(months=self.amc_duration) - relativedelta(days=1)
            self.amc_end_date = end_date
        else:
            self.amc_end_date = False

    def action_submit_amc(self):
        if self.is_amc_expired:
            raise UserError('AMC is already expired')
        self.amc_lines_ids._check_quantity_vs_identifications()
        if not self.amc_lines_ids:
            raise UserError('Please add at least one Service in AMC Details')
        # if self.amc_start_date < fields.Date.today():
        #     raise UserError('AMC Start Date must be greater than or equal to today')
        self.write({'state': 'to_approve'})

    def action_approve_amc(self):
        if self.is_amc_expired:
            raise UserError('AMC is already expired')
        self.amc_lines_ids._check_quantity_vs_identifications()
        if not self.amc_lines_ids:
            raise UserError('Please add at least one Service in AMC Details')
        self.write({'state': 'approved', 'is_locked': True})

    def action_lock_amc(self):
        if self.state == 'expired':
            raise UserError(_("Cannot lock an expired AMC Order."))
        self.write({'is_locked': True})

    def action_unlock_amc(self):
        if self.state == 'expired':
            raise UserError(_("Cannot unlock an expired AMC Order."))
        self.write({'is_locked': False})

    def action_cancel_amc(self):
        if self.is_amc_expired:
            raise UserError('AMC is already expired')
        self.write({'state': 'cancel'})

    def action_draft_amc(self):
        if self.state == 'expired':
            raise UserError(_("An expired AMC cannot be reset to draft. Please create a new AMC Order."))
        if self.state in ['approved', 'cancel']:
            self.write({'state': 'draft', 'is_locked': False})

    def action_send_amc_email(self):
        """Open email composer with AMC Approved template"""
        return self._open_amc_email_composer(
            template_xmlid='amc_mfx.email_template_amc_order',
            action_name=_('Send AMC Order'),
        )

    def action_send_amc_draft_email(self):
        """Open email composer with the Draft/Proposal template (shared with customer before approval)"""
        return self._open_amc_email_composer(
            template_xmlid='amc_mfx.email_template_amc_order_draft',
            action_name=_('Send AMC Proposal'),
        )

    def _open_amc_email_composer(self, template_xmlid, action_name):
        self.ensure_one()
        template_id = self.env.ref(template_xmlid, raise_if_not_found=False)
        if not template_id:
            raise UserError(_("Email template not found. Please contact administrator."))

        if not self.partner_email and not self.partner_id.email:
            raise UserError(_("Customer %s does not have an email address configured.") % self.partner_id.name)

        return {
            'type': 'ir.actions.act_window',
            'name': action_name,
            'res_model': 'mail.compose.message',
            'view_mode': 'form',
            'target': 'new',
            'context': {
                'default_model': 'amc.order',
                'default_res_ids': self.ids,
                'default_template_id': template_id.id,
                'default_composition_mode': 'comment',
                'mark_so_as_sent': True,
                'default_email_layout_xmlid': 'mail.mail_notification_light',
            },
        }

    @api.model
    def create(self, vals):
        if vals.get('name', _('New')) == _('New'):
            vals['name'] = self.env['ir.sequence'].next_by_code('amc.order') or _('New')
        return super(Amc, self).create(vals)

class AmcOrderLines(models.Model):
    _name = 'amc.order.lines'
    _description = 'AMC Order Lines'

    amc_id = fields.Many2one(comodel_name='amc.order', string='AMC')
    product_id = fields.Many2one(comodel_name='product.product', string='Product', domain="[('detailed_type', '!=', 'service')]", required=True)
    service_id = fields.Many2one(comodel_name='amc.services', string='Service Name')
    description = fields.Char('Description')
    quantity = fields.Float(string='Quantity', default=1.0)
    unit_price = fields.Float(string='Unit Price', default=1.0)
    tax_ids = fields.Many2many(comodel_name='account.tax', string='Taxes')
    currency_id = fields.Many2one(related='amc_id.currency_id', store=True, readonly=True)
    subtotal_price = fields.Monetary(string='Total (Excl. Taxes)', compute='_compute_amount', store=True, precompute=True)
    price_tax = fields.Float(string="Total Tax", compute='_compute_amount', store=True, precompute=True)
    total_price = fields.Monetary(string='Total (Incl. Taxes)', compute='_compute_amount', store=True, precompute=True)
    is_tracked = fields.Boolean(string='Tracked', compute='_compute_is_tracked', store=True, default=False)
    product_identification_ids = fields.Many2many(comodel_name='stock.lot', string='Identification Numbers', copy=False)
    location_id = fields.Many2one(comodel_name='stock.location', string='Location', default=lambda self: self.env['stock.location'].search([('name', '=', 'Customers')], limit=1))
    location = fields.Char(string='Location')
    remarks = fields.Char(string='Remarks')
    company_id = fields.Many2one(comodel_name='res.company', string='Company', default=lambda self: self.env.user.company_id.id)

    @api.depends('product_id')
    def _compute_is_tracked(self):
        for record in self:
            record.is_tracked = record.product_id.tracking != 'none'

    @api.onchange('service_id')
    def _onchange_service_id(self):
        if self.service_id:
            self.description = self.service_id.description

    @api.onchange('product_id')
    def _onchange_product_id(self):
        for rec in self:
            rec.product_identification_ids = False

    def _check_quantity_vs_identifications(self):
        """If product is tracked then product_identification_ids must be filled and match quantity."""
        for record in self:
            if record.is_tracked:
                # Must have at least one identification if tracked
                if not record.product_identification_ids:
                    raise ValidationError(_("You must select identification numbers for the tracked product %s.") % record.product_id.display_name)
                # Optional strict rule: quantity = number of identifications
                if len(record.product_identification_ids) != int(record.quantity):
                    raise ValidationError(_("Quantity (%s) must equal the number of identification numbers (%s) for the tracked product %s.") % (record.quantity, len(record.product_identification_ids), record.product_id.display_name))

    @api.depends('unit_price', 'quantity', 'tax_ids')
    def _compute_amount(self):
        """Compute untaxed and total (including taxes) prices."""
        for line in self:
            tax_results = self.env['account.tax'].with_company(line.company_id)._compute_taxes([
                line._convert_to_tax_base_line_dict()
            ])
            totals = list(tax_results['totals'].values())[0]
            amount_untaxed = totals['amount_untaxed']
            amount_tax = totals['amount_tax']

            line.update({
                'subtotal_price': amount_untaxed,
                'price_tax': amount_tax,
                'total_price': amount_untaxed + amount_tax,
            })

    def _convert_to_tax_base_line_dict(self, **kwargs):
        """ Convert the current record to a dictionary in order to use the generic taxes computation method
        defined on account.tax.

        :return: A python dictionary.
        """
        self.ensure_one()
        return self.env['account.tax']._convert_to_tax_base_line_dict(
            self,
            partner=self.amc_id.partner_id,
            currency=self.amc_id.currency_id,
            product=self.product_id,
            taxes=self.tax_ids,
            price_unit=self.unit_price,
            quantity=self.quantity,
            price_subtotal=self.subtotal_price,
            **kwargs,
        )

    @api.constrains('quantity', 'product_identification_ids')
    def _check_quantity_identification_on_save(self):
        """Validate quantity matches serial numbers when saving an approved AMC."""
        for record in self:
            if record.amc_id.state == 'approved' and record.is_tracked:
                if not record.product_identification_ids:
                    raise ValidationError(
                        _("You must select identification numbers for the tracked product %s.")
                        % record.product_id.display_name
                    )
                if len(record.product_identification_ids) != int(record.quantity):
                    raise ValidationError(
                        _("Quantity (%s) must equal the number of identification numbers (%s) for the tracked product %s.")
                        % (record.quantity, len(record.product_identification_ids), record.product_id.display_name)
                    )

    def write(self, vals):
        res = super().write(vals)
        if 'product_identification_ids' in vals:
            self._sync_lot_details()
        return res

    def _sync_lot_details(self):
        """Sync amc.lot.details when serial numbers change on an approved AMC line."""
        LotDetails = self.env['amc.lot.details']
        for line in self:
            if line.amc_id.state != 'approved':
                continue
            # Get current lot details for this line's AMC + product
            existing = LotDetails.search([
                ('amc_id', '=', line.amc_id.id),
                ('product_id', '=', line.product_id.id),
            ])
            existing_lot_ids = set(existing.mapped('lot_id').ids)
            current_lot_ids = set(line.product_identification_ids.ids)

            # Create missing lot details
            to_create = current_lot_ids - existing_lot_ids
            for lot_id in to_create:
                LotDetails.create({
                    'lot_id': lot_id,
                    'product_id': line.product_id.id,
                    'amc_id': line.amc_id.id,
                })

            # Remove lot details that are no longer in the line
            to_remove = existing_lot_ids - current_lot_ids
            if to_remove:
                existing.filtered(lambda r: r.lot_id.id in to_remove).unlink()

    @api.constrains('amc_id', 'product_id', 'service_id', 'location', 'product_identification_ids')
    def _check_duplicate_lines(self):
        for record in self:
            domain = [('amc_id', '=', record.amc_id.id), ('product_id', '=', record.product_id.id), ('service_id', '=', record.service_id.id), ('location', '=', record.location), ('id', '!=', record.id)]
            existing_lines = self.search(domain)
            for line in existing_lines:
                if set(line.product_identification_ids.ids) & set(record.product_identification_ids.ids):
                    raise UserError(_("A line with Product '%s', Service '%s', Location '%s', and the same Identification numbers already exists for this AMC.") % (record.product_id.name, record.service_id.name, record.location))