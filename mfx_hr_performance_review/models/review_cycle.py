from datetime import timedelta

from odoo import api, fields, models, _
from odoo.exceptions import ValidationError


class ReviewCycle(models.Model):
    _name = 'hr.review.cycle'
    _description = 'Performance Review Cycle'
    _inherit = ['mail.thread', 'mail.activity.mixin']
    _order = 'date_start desc'

    name = fields.Char(
        string='Cycle Name',
        required=True,
        tracking=True,
    )
    cycle_type = fields.Selection([
        ('quarterly', 'Quarterly'),
        ('semi_annual', 'Semi-Annual'),
        ('annual', 'Annual'),
        ('custom', 'Custom'),
    ], string='Cycle Type', required=True, default='annual', tracking=True)
    date_start = fields.Date(
        string='Start Date',
        required=True,
        tracking=True,
    )
    date_end = fields.Date(
        string='End Date',
        required=True,
        tracking=True,
    )
    self_review_deadline = fields.Date(
        string='Self-Review Deadline',
        tracking=True,
    )
    manager_review_deadline = fields.Date(
        string='Manager Review Deadline',
        tracking=True,
    )
    template_id = fields.Many2one(
        'hr.review.template',
        string='Review Template',
        required=True,
        tracking=True,
    )
    department_ids = fields.Many2many(
        'hr.department',
        string='Departments',
        help='Leave empty to include all departments.',
    )
    state = fields.Selection([
        ('draft', 'Draft'),
        ('in_progress', 'In Progress'),
        ('done', 'Completed'),
        ('cancelled', 'Cancelled'),
    ], string='Status', default='draft', tracking=True, required=True)
    review_ids = fields.One2many(
        'hr.performance.review',
        'cycle_id',
        string='Reviews',
    )
    review_count = fields.Integer(
        string='Review Count',
        compute='_compute_review_count',
    )
    company_id = fields.Many2one(
        'res.company',
        string='Company',
        default=lambda self: self.env.company,
        required=True,
    )
    note = fields.Html(string='Notes')

    @api.depends('review_ids')
    def _compute_review_count(self):
        for cycle in self:
            cycle.review_count = len(cycle.review_ids)

    @api.constrains('date_start', 'date_end')
    def _check_dates(self):
        for cycle in self:
            if cycle.date_start and cycle.date_end and cycle.date_start > cycle.date_end:
                raise ValidationError(_('End Date must be after Start Date.'))

    @api.constrains('self_review_deadline', 'manager_review_deadline', 'date_start', 'date_end')
    def _check_deadlines(self):
        for cycle in self:
            if cycle.self_review_deadline:
                if cycle.self_review_deadline < cycle.date_start:
                    raise ValidationError(
                        _('Self-Review Deadline must be after the cycle Start Date.'))
            if cycle.manager_review_deadline:
                if cycle.manager_review_deadline < cycle.date_start:
                    raise ValidationError(
                        _('Manager Review Deadline must be after the cycle Start Date.'))

    def action_start(self):
        self.ensure_one()
        if not self.review_ids:
            raise ValidationError(
                _('Please generate reviews before starting the cycle. '
                  'Use the "Generate Reviews" button.'))
        self.write({'state': 'in_progress'})
        for review in self.review_ids.filtered(lambda r: r.state == 'draft'):
            review.action_start_self_review()

    def action_complete(self):
        self.ensure_one()
        pending = self.review_ids.filtered(lambda r: r.state not in ('done', 'cancelled'))
        if pending:
            raise ValidationError(
                _('Cannot complete cycle. %d review(s) are still pending.') % len(pending))
        self.write({'state': 'done'})

    def action_cancel(self):
        self.ensure_one()
        self.write({'state': 'cancelled'})
        for review in self.review_ids.filtered(lambda r: r.state != 'done'):
            review.write({'state': 'cancelled'})

    def action_reset_to_draft(self):
        self.ensure_one()
        self.write({'state': 'draft'})

    def action_view_reviews(self):
        self.ensure_one()
        return {
            'type': 'ir.actions.act_window',
            'name': _('Performance Reviews'),
            'res_model': 'hr.performance.review',
            'view_mode': 'tree,form,kanban',
            'domain': [('cycle_id', '=', self.id)],
            'context': {'default_cycle_id': self.id},
        }

    def action_generate_reviews(self):
        self.ensure_one()
        return {
            'type': 'ir.actions.act_window',
            'name': _('Generate Reviews'),
            'res_model': 'hr.generate.reviews.wizard',
            'view_mode': 'form',
            'target': 'new',
            'context': {'default_cycle_id': self.id},
        }

    @api.model
    def _cron_send_deadline_reminders(self):
        """Send reminders 3 days before self-review and manager review deadlines."""
        today = fields.Date.context_today(self)
        reminder_date = today + timedelta(days=3)

        # Self-review deadline reminders
        cycles_self = self.search([
            ('state', '=', 'in_progress'),
            ('self_review_deadline', '=', reminder_date),
        ])
        for cycle in cycles_self:
            pending_reviews = cycle.review_ids.filtered(
                lambda r: r.state == 'self_review')
            for review in pending_reviews:
                review.message_post(
                    body=_('Reminder: Your self-review deadline is in 3 days (%s). '
                           'Please complete your self-assessment.') % cycle.self_review_deadline,
                    partner_ids=review.employee_id.user_id.partner_id.ids,
                    message_type='notification',
                    subtype_xmlid='mail.mt_note',
                )

        # Manager review deadline reminders
        cycles_mgr = self.search([
            ('state', '=', 'in_progress'),
            ('manager_review_deadline', '=', reminder_date),
        ])
        for cycle in cycles_mgr:
            pending_reviews = cycle.review_ids.filtered(
                lambda r: r.state == 'manager_review')
            for review in pending_reviews:
                if review.manager_id and review.manager_id.user_id:
                    review.message_post(
                        body=_('Reminder: Manager review deadline is in 3 days (%s). '
                               'Please complete the review for %s.') % (
                                   cycle.manager_review_deadline,
                                   review.employee_id.name),
                        partner_ids=review.manager_id.user_id.partner_id.ids,
                        message_type='notification',
                        subtype_xmlid='mail.mt_note',
                    )
