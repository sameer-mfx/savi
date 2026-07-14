from odoo import api, fields, models, _
from odoo.exceptions import ValidationError


class ReviewGoal(models.Model):
    _name = 'hr.review.goal'
    _description = 'Employee Performance Goal'
    _inherit = ['mail.thread']
    _order = 'deadline, id'

    name = fields.Char(
        string='Goal Title',
        required=True,
        tracking=True,
    )
    description = fields.Text(string='Description')
    employee_id = fields.Many2one(
        'hr.employee',
        string='Employee',
        required=True,
        tracking=True,
    )
    review_id = fields.Many2one(
        'hr.performance.review',
        string='Performance Review',
        ondelete='set null',
    )
    manager_id = fields.Many2one(
        'hr.employee',
        string='Assigned By',
        default=lambda self: self.env.user.employee_id,
    )
    goal_type = fields.Selection([
        ('performance', 'Performance'),
        ('development', 'Development'),
        ('project', 'Project'),
        ('learning', 'Learning'),
        ('behavioral', 'Behavioral'),
    ], string='Goal Type', default='performance', required=True)
    priority = fields.Selection([
        ('0', 'Low'),
        ('1', 'Medium'),
        ('2', 'High'),
        ('3', 'Critical'),
    ], string='Priority', default='1')
    deadline = fields.Date(
        string='Deadline',
        tracking=True,
    )
    progress = fields.Float(
        string='Progress (%)',
        default=0.0,
        tracking=True,
    )
    metric = fields.Char(
        string='Success Metric',
        help='How this goal will be measured (e.g., "Close 10 deals", "Complete certification")',
    )
    state = fields.Selection([
        ('draft', 'Draft'),
        ('in_progress', 'In Progress'),
        ('achieved', 'Achieved'),
        ('partially_achieved', 'Partially Achieved'),
        ('not_achieved', 'Not Achieved'),
        ('cancelled', 'Cancelled'),
    ], string='Status', default='draft', tracking=True, required=True)
    employee_notes = fields.Text(string='Employee Notes')
    manager_notes = fields.Text(string='Manager Notes')
    company_id = fields.Many2one(
        'res.company',
        string='Company',
        default=lambda self: self.env.company,
        required=True,
    )

    @api.constrains('progress')
    def _check_progress(self):
        for goal in self:
            if goal.progress < 0 or goal.progress > 100:
                raise ValidationError(
                    _('Progress must be between 0 and 100.'))

    def action_start(self):
        self.write({'state': 'in_progress'})

    def action_achieve(self):
        self.write({'state': 'achieved', 'progress': 100.0})

    def action_partial(self):
        self.write({'state': 'partially_achieved'})

    def action_fail(self):
        self.write({'state': 'not_achieved'})

    def action_cancel(self):
        self.write({'state': 'cancelled'})

    def action_reset(self):
        self.write({'state': 'draft', 'progress': 0.0})
