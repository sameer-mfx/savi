from odoo import models, fields, api, _
from odoo.exceptions import UserError


class AmcReplacement(models.Model):
    _name = 'amc.replacement'
    _description = 'AMC Replacement'
    _order = 'issue_date desc, id desc'
    _inherit = ['mail.thread', 'mail.activity.mixin']

    amc_id = fields.Many2one(
        comodel_name='amc.order',
        string='AMC Order',
        required=True,
        ondelete='cascade',
        tracking=True,
    )
    amc_state = fields.Selection(related='amc_id.state', store=True)
    amc_is_locked = fields.Boolean(related='amc_id.is_locked', store=True)
    amc_is_expired = fields.Boolean(related='amc_id.is_amc_expired')
    partner_id = fields.Many2one(related='amc_id.partner_id', store=True, readonly=True)
    visit_id = fields.Many2one(
        comodel_name='amc.site.visit',
        string='Site Visit',
        domain="[('amc_order_id', '=', amc_id)]",
        tracking=True,
    )
    issue_date = fields.Date(string='Issue Date', default=fields.Date.context_today, required=True, tracking=True)
    faulty_product_id = fields.Many2one(
        comodel_name='product.product',
        string='Faulty Product',
        tracking=True,
    )
    faulty_lot_id = fields.Many2one(
        comodel_name='stock.lot',
        string='Faulty Serial/Lot',
        domain="[('product_id', '=', faulty_product_id)]",
    )
    issued_product_id = fields.Many2one(
        comodel_name='product.product',
        string='Issued Product',
        required=True,
        tracking=True,
    )
    issued_lot_id = fields.Many2one(
        comodel_name='stock.lot',
        string='Issued Serial/Lot',
        domain="[('product_id', '=', issued_product_id)]",
    )
    quantity = fields.Float(string='Quantity', default=1.0, required=True)
    unit_cost = fields.Float(
        string='Unit Cost',
        help='Cost of the product issued. Defaults to product standard price.',
    )
    total_cost = fields.Monetary(
        string='Total Cost',
        compute='_compute_total_cost',
        store=True,
        currency_field='currency_id',
    )
    currency_id = fields.Many2one(related='amc_id.currency_id', store=True, readonly=True)
    state = fields.Selection(
        selection=[
            ('draft', 'Draft'),
            ('to_approve', 'To Approve'),
            ('approved', 'Approved'),
            ('rejected', 'Rejected'),
            ('issued', 'Issued'),
            ('done', 'Done'),
            ('cancel', 'Cancelled'),
        ],
        default='draft',
        tracking=True,
        required=True,
    )
    approved_by = fields.Many2one('res.users', string='Approved By', readonly=True, copy=False)
    approved_date = fields.Datetime(string='Approval Date', readonly=True, copy=False)
    rejection_reason = fields.Text(string='Rejection Reason', copy=False)
    note = fields.Text(string='Remarks')
    company_id = fields.Many2one(
        comodel_name='res.company',
        string='Company',
        default=lambda self: self.env.company,
    )

    @api.depends('quantity', 'unit_cost')
    def _compute_total_cost(self):
        for rec in self:
            rec.total_cost = rec.quantity * rec.unit_cost

    @api.onchange('issued_product_id')
    def _onchange_issued_product_id(self):
        if self.issued_product_id and not self.unit_cost:
            self.unit_cost = self.issued_product_id.standard_price

    @api.onchange('visit_id')
    def _onchange_visit_id(self):
        if self.visit_id and self.visit_id.amc_order_id and not self.amc_id:
            self.amc_id = self.visit_id.amc_order_id

    def _check_amc_not_expired(self):
        """Block creating records against a non-approved (including expired) AMC."""
        for rec in self:
            if rec.amc_id.state != 'approved':
                raise UserError(_(
                    "Replacements can only be added to an approved AMC Order. "
                    "'%s' is currently: %s."
                ) % (rec.amc_id.name, dict(rec.amc_id._fields['state'].selection).get(rec.amc_id.state, rec.amc_id.state)))

    @api.model_create_multi
    def create(self, vals_list):
        records = super().create(vals_list)
        records._check_amc_not_expired()
        return records

    def write(self, vals):
        if 'amc_id' in vals:
            new_amc = self.env['amc.order'].browse(vals['amc_id'])
            if new_amc.state != 'approved':
                raise UserError(_(
                    "Cannot re-assign this replacement to a non-approved AMC Order '%s'."
                ) % new_amc.name)
        return super().write(vals)

    def unlink(self):
        for rec in self:
            if rec.amc_id.state == 'expired':
                raise UserError(_(
                    "Cannot delete a replacement linked to expired AMC Order '%s'."
                ) % rec.amc_id.name)
        return super().unlink()

    def action_submit(self):
        self._check_amc_not_expired()
        for rec in self:
            if not rec.visit_id:
                raise UserError(_("A site visit must be linked before submitting this replacement for approval."))
            if not rec.issued_product_id:
                raise UserError(_("Issued Product is required before submitting for approval."))
        self.write({'state': 'to_approve'})

    def action_approve(self):
        if not self.env.user.has_group('amc_mfx.amc_group_manager'):
            raise UserError(_("Only AMC Managers can approve replacements."))
        self.write({
            'state': 'approved',
            'approved_by': self.env.user.id,
            'approved_date': fields.Datetime.now(),
            'rejection_reason': False,
        })

    def action_reject(self):
        if not self.env.user.has_group('amc_mfx.amc_group_manager'):
            raise UserError(_("Only AMC Managers can reject replacements."))
        self.write({'state': 'rejected'})

    def action_issue(self):
        for rec in self:
            if rec.state not in ('approved', 'issued'):
                raise UserError(_(
                    "Replacement must be Approved before it can be issued. "
                    "Current status: %s."
                ) % dict(rec._fields['state'].selection).get(rec.state, rec.state))
        self.write({'state': 'issued'})

    def action_done(self):
        self.write({'state': 'done'})

    def action_cancel(self):
        self.write({'state': 'cancel'})

    def action_draft(self):
        self.write({
            'state': 'draft',
            'approved_by': False,
            'approved_date': False,
            'rejection_reason': False,
        })


class AmcExpense(models.Model):
    _name = 'amc.expense'
    _description = 'AMC Expense'
    _order = 'expense_date desc, id desc'
    _inherit = ['mail.thread', 'mail.activity.mixin']

    amc_id = fields.Many2one(
        comodel_name='amc.order',
        string='AMC Order',
        required=True,
        ondelete='cascade',
        tracking=True,
    )
    amc_state = fields.Selection(related='amc_id.state', store=True)
    amc_is_locked = fields.Boolean(related='amc_id.is_locked', store=True)
    partner_id = fields.Many2one(related='amc_id.partner_id', store=True, readonly=True)
    visit_id = fields.Many2one(
        comodel_name='amc.site.visit',
        string='Site Visit',
        domain="[('amc_order_id', '=', amc_id)]",
    )
    expense_type = fields.Selection(
        selection=[
            ('visit', 'Engineer Visit'),
            ('travel', 'Travel / Conveyance'),
            ('replacement', 'Replacement Part/Product'),
            ('consumable', 'Consumables'),
            ('labour', 'Labour / Service'),
            ('other', 'Other'),
        ],
        string='Expense Type',
        required=True,
        default='visit',
        tracking=True,
    )
    replacement_id = fields.Many2one(
        comodel_name='amc.replacement',
        string='Related Replacement',
        domain="[('amc_id', '=', amc_id)]",
    )
    description = fields.Char(string='Description', required=True)
    expense_date = fields.Date(string='Expense Date', default=fields.Date.context_today, required=True)
    engineer_id = fields.Many2one(comodel_name='res.users', string='Engineer')
    amount = fields.Monetary(string='Amount', required=True, currency_field='currency_id', tracking=True)
    currency_id = fields.Many2one(related='amc_id.currency_id', store=True, readonly=True)
    company_id = fields.Many2one(
        comodel_name='res.company',
        string='Company',
        default=lambda self: self.env.company,
    )
    state = fields.Selection(
        selection=[
            ('draft', 'Draft'),
            ('to_approve', 'To Approve'),
            ('approved', 'Approved'),
            ('rejected', 'Rejected'),
            ('confirmed', 'Confirmed'),
            ('cancel', 'Cancelled'),
        ],
        default='draft',
        tracking=True,
    )
    approved_by = fields.Many2one('res.users', string='Approved By', readonly=True, copy=False)
    approved_date = fields.Datetime(string='Approval Date', readonly=True, copy=False)
    rejection_reason = fields.Text(string='Rejection Reason', copy=False)
    note = fields.Text(string='Remarks')

    @api.onchange('visit_id')
    def _onchange_visit_id(self):
        if self.visit_id and self.visit_id.amc_order_id and not self.amc_id:
            self.amc_id = self.visit_id.amc_order_id

    def _check_amc_not_expired(self):
        """Block creating records against a non-approved (including expired) AMC."""
        for rec in self:
            if rec.amc_id.state != 'approved':
                raise UserError(_(
                    "Expenses can only be added to an approved AMC Order. "
                    "'%s' is currently: %s."
                ) % (rec.amc_id.name, dict(rec.amc_id._fields['state'].selection).get(rec.amc_id.state, rec.amc_id.state)))

    @api.model_create_multi
    def create(self, vals_list):
        records = super().create(vals_list)
        records._check_amc_not_expired()
        return records

    def write(self, vals):
        if 'amc_id' in vals:
            new_amc = self.env['amc.order'].browse(vals['amc_id'])
            if new_amc.state != 'approved':
                raise UserError(_(
                    "Cannot re-assign this expense to a non-approved AMC Order '%s'."
                ) % new_amc.name)
        return super().write(vals)

    def unlink(self):
        for rec in self:
            if rec.amc_id.state == 'expired':
                raise UserError(_(
                    "Cannot delete an expense linked to expired AMC Order '%s'."
                ) % rec.amc_id.name)
        return super().unlink()

    def action_submit(self):
        self._check_amc_not_expired()
        for rec in self:
            if not rec.visit_id:
                raise UserError(_("A site visit must be linked before submitting this expense for approval."))
        self.write({'state': 'to_approve'})

    def action_approve(self):
        if not self.env.user.has_group('amc_mfx.amc_group_manager'):
            raise UserError(_("Only AMC Managers can approve expenses."))
        self.write({
            'state': 'approved',
            'approved_by': self.env.user.id,
            'approved_date': fields.Datetime.now(),
            'rejection_reason': False,
        })

    def action_reject(self):
        if not self.env.user.has_group('amc_mfx.amc_group_manager'):
            raise UserError(_("Only AMC Managers can reject expenses."))
        self.write({'state': 'rejected'})

    def action_confirm(self):
        for rec in self:
            if rec.state not in ('approved', 'confirmed'):
                raise UserError(_(
                    "Expense must be Approved before it can be Confirmed. Current status: %s."
                ) % dict(rec._fields['state'].selection).get(rec.state, rec.state))
        self.write({'state': 'confirmed'})

    def action_cancel(self):
        self.write({'state': 'cancel'})

    def action_draft(self):
        self.write({
            'state': 'draft',
            'approved_by': False,
            'approved_date': False,
            'rejection_reason': False,
        })


class AmcOrder(models.Model):
    _inherit = 'amc.order'

    replacement_ids = fields.One2many(
        comodel_name='amc.replacement',
        inverse_name='amc_id',
        string='Replacements',
    )
    expense_ids = fields.One2many(
        comodel_name='amc.expense',
        inverse_name='amc_id',
        string='Expenses',
    )
    replacement_count = fields.Integer(compute='_compute_replacement_count')
    expense_count = fields.Integer(compute='_compute_expense_count')
    pending_replacement_count = fields.Integer(compute='_compute_pending_counts')
    pending_expense_count = fields.Integer(compute='_compute_pending_counts')

    total_revenue = fields.Monetary(
        string='AMC Revenue',
        compute='_compute_pnl',
        store=True,
        help='Total AMC contract value (untaxed).',
    )
    total_replacement_cost = fields.Monetary(
        string='Replacement Cost',
        compute='_compute_pnl',
        store=True,
    )
    total_expense_cost = fields.Monetary(
        string='Other Expenses',
        compute='_compute_pnl',
        store=True,
    )
    total_cost = fields.Monetary(
        string='Total Cost',
        compute='_compute_pnl',
        store=True,
    )
    profit_amount = fields.Monetary(
        string='Profit / Loss',
        compute='_compute_pnl',
        store=True,
    )
    profit_margin = fields.Float(
        string='Profit Margin (%)',
        compute='_compute_pnl',
        store=True,
    )

    @api.depends(
        'amount_untaxed',
        'replacement_ids.total_cost',
        'replacement_ids.state',
        'expense_ids.amount',
        'expense_ids.state',
    )
    def _compute_pnl(self):
        for rec in self:
            replacement_cost = sum(
                r.total_cost for r in rec.replacement_ids
                if r.state in ('approved', 'issued', 'done')
            )
            expense_cost = sum(
                e.amount for e in rec.expense_ids
                if e.state in ('approved', 'confirmed')
            )
            total_cost = replacement_cost + expense_cost
            revenue = rec.amount_untaxed or 0.0

            rec.total_revenue = revenue
            rec.total_replacement_cost = replacement_cost
            rec.total_expense_cost = expense_cost
            rec.total_cost = total_cost
            rec.profit_amount = revenue - total_cost
            rec.profit_margin = (rec.profit_amount / revenue * 100.0) if revenue else 0.0

    def _compute_replacement_count(self):
        for rec in self:
            rec.replacement_count = len(rec.replacement_ids)

    def _compute_expense_count(self):
        for rec in self:
            rec.expense_count = len(rec.expense_ids)

    @api.depends('replacement_ids.state', 'expense_ids.state')
    def _compute_pending_counts(self):
        for rec in self:
            rec.pending_replacement_count = len(rec.replacement_ids.filtered(lambda r: r.state == 'to_approve'))
            rec.pending_expense_count = len(rec.expense_ids.filtered(lambda e: e.state == 'to_approve'))

    def action_view_replacements(self):
        self.ensure_one()
        return {
            'type': 'ir.actions.act_window',
            'name': _('Replacements'),
            'res_model': 'amc.replacement',
            'view_mode': 'tree,form',
            'domain': [('amc_id', '=', self.id)],
            'context': {'default_amc_id': self.id},
        }

    def action_view_expenses(self):
        self.ensure_one()
        return {
            'type': 'ir.actions.act_window',
            'name': _('AMC Expenses'),
            'res_model': 'amc.expense',
            'view_mode': 'tree,form',
            'domain': [('amc_id', '=', self.id)],
            'context': {'default_amc_id': self.id},
        }

    def action_view_pending_approvals(self):
        self.ensure_one()
        return {
            'type': 'ir.actions.act_window',
            'name': _('Pending Replacement Approvals'),
            'res_model': 'amc.replacement',
            'view_mode': 'tree,form',
            'domain': [('amc_id', '=', self.id), ('state', '=', 'to_approve')],
            'context': {'default_amc_id': self.id},
        }
