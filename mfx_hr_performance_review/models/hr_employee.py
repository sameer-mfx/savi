from odoo import api, fields, models, _


class HrEmployee(models.Model):
    _inherit = 'hr.employee'

    hr_review_rating = fields.Float(
        string='HR Review Rating',
        digits=(4, 2),
        help='Latest HR performance review rating (0-5 scale).',
    )
    review_ids = fields.One2many(
        'hr.performance.review',
        'employee_id',
        string='Performance Reviews',
    )
    review_count = fields.Integer(
        string='Review Count',
        compute='_compute_review_count',
    )
    goal_ids = fields.One2many(
        'hr.review.goal',
        'employee_id',
        string='Goals',
    )
    goal_count = fields.Integer(
        string='Goal Count',
        compute='_compute_goal_count',
    )
    last_review_date = fields.Date(
        string='Last Review Date',
        compute='_compute_last_review',
        store=True,
    )
    last_review_rating = fields.Float(
        string='Last Review Rating',
        compute='_compute_last_review',
        store=True,
        digits=(4, 2),
    )
    average_rating = fields.Float(
        string='Average Rating',
        compute='_compute_average_rating',
        store=True,
        digits=(4, 2),
        help='Average of all completed performance review final ratings.',
    )

    @api.depends('review_ids')
    def _compute_review_count(self):
        for employee in self:
            employee.review_count = len(employee.review_ids)

    @api.depends('goal_ids')
    def _compute_goal_count(self):
        for employee in self:
            employee.goal_count = len(employee.goal_ids)

    @api.depends('review_ids.state', 'review_ids.final_rating', 'review_ids.date_review')
    def _compute_last_review(self):
        for employee in self:
            completed_reviews = employee.review_ids.filtered(
                lambda r: r.state == 'done'
            ).sorted('date_review', reverse=True)
            if completed_reviews:
                employee.last_review_date = completed_reviews[0].date_review
                employee.last_review_rating = completed_reviews[0].final_rating
            else:
                employee.last_review_date = False
                employee.last_review_rating = 0.0

    @api.depends('review_ids.state', 'review_ids.final_rating')
    def _compute_average_rating(self):
        for employee in self:
            completed_reviews = employee.review_ids.filtered(
                lambda r: r.state == 'done' and r.final_rating > 0
            )
            if completed_reviews:
                employee.average_rating = sum(
                    completed_reviews.mapped('final_rating')
                ) / len(completed_reviews)
            else:
                employee.average_rating = 0.0

    def action_view_reviews(self):
        self.ensure_one()
        return {
            'type': 'ir.actions.act_window',
            'name': _('Performance Reviews'),
            'res_model': 'hr.performance.review',
            'view_mode': 'tree,form',
            'domain': [('employee_id', '=', self.id)],
            'context': {'default_employee_id': self.id},
        }

    def action_view_goals(self):
        self.ensure_one()
        return {
            'type': 'ir.actions.act_window',
            'name': _('Goals'),
            'res_model': 'hr.review.goal',
            'view_mode': 'tree,form',
            'domain': [('employee_id', '=', self.id)],
            'context': {'default_employee_id': self.id},
        }
