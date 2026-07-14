from odoo import api, fields, models, _
from odoo.exceptions import UserError, ValidationError


class PerformanceReview(models.Model):
    _name = 'hr.performance.review'
    _description = 'Employee Performance Review'
    _inherit = ['mail.thread', 'mail.activity.mixin']
    _order = 'create_date desc'
    _rec_name = 'display_name'

    name = fields.Char(
        string='Reference',
        readonly=True,
        copy=False,
        default='New',
    )
    display_name = fields.Char(
        compute='_compute_display_name',
        store=True,
    )
    employee_id = fields.Many2one(
        'hr.employee',
        string='Employee',
        required=True,
        tracking=True,
    )
    department_id = fields.Many2one(
        'hr.department',
        string='Department',
        related='employee_id.department_id',
        store=True,
        readonly=True,
    )
    job_id = fields.Many2one(
        'hr.job',
        string='Job Position',
        related='employee_id.job_id',
        store=True,
        readonly=True,
    )
    manager_id = fields.Many2one(
        'hr.employee',
        string='Reviewer (Manager)',
        tracking=True,
    )
    cycle_id = fields.Many2one(
        'hr.review.cycle',
        string='Review Cycle',
        tracking=True,
        ondelete='cascade',
    )
    template_id = fields.Many2one(
        'hr.review.template',
        string='Review Template',
        related='cycle_id.template_id',
        store=True,
        readonly=True,
    )
    date_review = fields.Date(
        string='Review Date',
        default=fields.Date.context_today,
        tracking=True,
    )
    date_start = fields.Date(
        string='Period Start',
        related='cycle_id.date_start',
        store=True,
        readonly=True,
    )
    date_end = fields.Date(
        string='Period End',
        related='cycle_id.date_end',
        store=True,
        readonly=True,
    )

    # Rating lines
    rating_line_ids = fields.One2many(
        'hr.performance.review.line',
        'review_id',
        string='Evaluation Ratings',
    )

    # Scores
    self_rating = fields.Float(
        string='Self Rating',
        compute='_compute_ratings',
        store=True,
        digits=(4, 2),
    )
    manager_rating = fields.Float(
        string='Manager Rating',
        compute='_compute_ratings',
        store=True,
        digits=(4, 2),
    )
    final_rating = fields.Float(
        string='Final Rating',
        compute='_compute_final_rating',
        store=True,
        digits=(4, 2),
        tracking=True,
    )
    final_rating_label = fields.Char(
        string='Performance Level',
        compute='_compute_final_rating',
        store=True,
    )

    # Textual feedback
    self_summary = fields.Text(string='Employee Self-Assessment Summary')
    self_strengths = fields.Text(string='Self-Identified Strengths')
    self_improvements = fields.Text(string='Areas for Improvement (Self)')
    manager_summary = fields.Text(string='Manager Assessment Summary')
    manager_strengths = fields.Text(string='Strengths (Manager)')
    manager_improvements = fields.Text(string='Areas for Improvement (Manager)')
    hr_comments = fields.Text(string='HR Comments')

    # Goals
    goal_ids = fields.One2many(
        'hr.review.goal',
        'review_id',
        string='Goals',
    )
    goal_achievement_rate = fields.Float(
        string='Goal Achievement (%)',
        compute='_compute_goal_achievement',
        store=True,
        digits=(5, 2),
    )

    # State
    state = fields.Selection([
        ('draft', 'Draft'),
        ('self_review', 'Self-Review'),
        ('manager_review', 'Manager Review'),
        ('hr_review', 'HR Review'),
        ('done', 'Completed'),
        ('cancelled', 'Cancelled'),
    ], string='Status', default='draft', tracking=True, required=True)

    company_id = fields.Many2one(
        'res.company',
        string='Company',
        default=lambda self: self.env.company,
        required=True,
    )

    @api.depends('employee_id', 'name')
    def _compute_display_name(self):
        for review in self:
            if review.employee_id and review.name:
                review.display_name = '%s - %s' % (review.name, review.employee_id.name)
            elif review.employee_id:
                review.display_name = review.employee_id.name
            else:
                review.display_name = review.name or ''

    @api.model_create_multi
    def create(self, vals_list):
        for vals in vals_list:
            if vals.get('name', 'New') == 'New':
                vals['name'] = self.env['ir.sequence'].next_by_code(
                    'hr.performance.review') or 'New'
        reviews = super().create(vals_list)
        for review in reviews:
            if not review.rating_line_ids and review.template_id:
                review._generate_rating_lines()
        return reviews

    def _generate_rating_lines(self):
        self.ensure_one()
        lines = []
        for criteria in self.template_id.criteria_ids:
            lines.append((0, 0, {
                'criteria_id': criteria.id,
                'weight': criteria.weight,
            }))
        if lines:
            self.write({'rating_line_ids': lines})

    @api.depends('rating_line_ids.self_score', 'rating_line_ids.manager_score',
                 'rating_line_ids.weight')
    def _compute_ratings(self):
        for review in self:
            lines = review.rating_line_ids
            total_weight = sum(lines.mapped('weight')) or 1.0
            self_weighted = sum(
                line.self_score * line.weight for line in lines
            )
            manager_weighted = sum(
                line.manager_score * line.weight for line in lines
            )
            review.self_rating = self_weighted / total_weight
            review.manager_rating = manager_weighted / total_weight

    @api.depends('self_rating', 'manager_rating', 'goal_achievement_rate')
    def _compute_final_rating(self):
        for review in self:
            if review.manager_rating > 0:
                goal_score = (review.goal_achievement_rate / 100.0) * 5.0
                review.final_rating = (
                    review.manager_rating * 0.70
                    + review.self_rating * 0.20
                    + goal_score * 0.10
                )
            elif review.self_rating > 0:
                review.final_rating = review.self_rating
            else:
                review.final_rating = 0.0

            rating = review.final_rating
            if rating >= 4.5:
                review.final_rating_label = 'Outstanding'
            elif rating >= 3.5:
                review.final_rating_label = 'Exceeds Expectations'
            elif rating >= 2.5:
                review.final_rating_label = 'Meets Expectations'
            elif rating >= 1.5:
                review.final_rating_label = 'Below Expectations'
            elif rating > 0:
                review.final_rating_label = 'Needs Improvement'
            else:
                review.final_rating_label = False

    @api.depends('goal_ids.progress')
    def _compute_goal_achievement(self):
        for review in self:
            goals = review.goal_ids
            if goals:
                review.goal_achievement_rate = sum(
                    goals.mapped('progress')) / len(goals)
            else:
                review.goal_achievement_rate = 0.0

    # ── Workflow Actions ────────────────────────────────────────

    def action_start_self_review(self):
        for review in self:
            if review.state != 'draft':
                raise UserError(_('Only draft reviews can be sent for self-review.'))
            review.write({'state': 'self_review'})
            template = self.env.ref(
                'mfx_hr_performance_review.mail_template_self_review',
                raise_if_not_found=False)
            if template:
                template.send_mail(review.id, force_send=False)

    def action_submit_self_review(self):
        for review in self:
            if review.state != 'self_review':
                raise UserError(
                    _('Only reviews in self-review stage can be submitted.'))
            review.write({'state': 'manager_review'})
            template = self.env.ref(
                'mfx_hr_performance_review.mail_template_manager_review',
                raise_if_not_found=False)
            if template:
                template.send_mail(review.id, force_send=False)

    def action_submit_manager_review(self):
        for review in self:
            if review.state != 'manager_review':
                raise UserError(
                    _('Only reviews in manager review stage can be submitted.'))
            review.write({'state': 'hr_review'})

    def action_approve(self):
        for review in self:
            if review.state != 'hr_review':
                raise UserError(
                    _('Only reviews in HR review stage can be approved.'))
            review.write({'state': 'done'})
            if review.final_rating > 0 and review.employee_id:
                review.employee_id.sudo().write({
                    'hr_review_rating': review.final_rating,
                })
            template = self.env.ref(
                'mfx_hr_performance_review.mail_template_review_completed',
                raise_if_not_found=False)
            if template:
                template.send_mail(review.id, force_send=False)

    def action_cancel(self):
        for review in self:
            review.write({'state': 'cancelled'})

    def action_reset_to_draft(self):
        for review in self:
            review.write({'state': 'draft'})


class PerformanceReviewLine(models.Model):
    _name = 'hr.performance.review.line'
    _description = 'Performance Review Rating Line'
    _order = 'sequence, id'

    review_id = fields.Many2one(
        'hr.performance.review',
        string='Review',
        required=True,
        ondelete='cascade',
    )
    criteria_id = fields.Many2one(
        'hr.review.criteria',
        string='Criteria',
        required=True,
    )
    criteria_description = fields.Text(
        related='criteria_id.description',
        string='Description',
        readonly=True,
    )
    criteria_category = fields.Selection(
        related='criteria_id.category',
        string='Category',
        store=True,
    )
    weight = fields.Float(
        string='Weight (%)',
        digits=(5, 2),
    )
    sequence = fields.Integer(
        related='criteria_id.sequence',
        store=True,
    )

    # Self-assessment (float 0-5)
    self_score = fields.Float(
        string='Self Score',
        default=0.0,
        digits=(3, 1),
    )
    self_comment = fields.Text(string='Self Comment')

    # Manager assessment (float 0-5)
    manager_score = fields.Float(
        string='Manager Score',
        default=0.0,
        digits=(3, 1),
    )
    manager_comment = fields.Text(string='Manager Comment')

    @api.constrains('self_score', 'manager_score')
    def _check_scores(self):
        for line in self:
            if line.self_score < 0 or line.self_score > 5:
                raise ValidationError(
                    _('Self score must be between 0 and 5.'))
            if line.manager_score < 0 or line.manager_score > 5:
                raise ValidationError(
                    _('Manager score must be between 0 and 5.'))
