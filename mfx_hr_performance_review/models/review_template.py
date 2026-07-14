from odoo import api, fields, models, _
from odoo.exceptions import ValidationError


class ReviewTemplate(models.Model):
    _name = 'hr.review.template'
    _description = 'Performance Review Template'
    _order = 'name'

    name = fields.Char(
        string='Template Name',
        required=True,
    )
    description = fields.Text(string='Description')
    active = fields.Boolean(default=True)
    criteria_ids = fields.One2many(
        'hr.review.criteria',
        'template_id',
        string='Evaluation Criteria',
    )
    department_ids = fields.Many2many(
        'hr.department',
        string='Applicable Departments',
        help='Leave empty to apply to all departments.',
    )
    job_ids = fields.Many2many(
        'hr.job',
        string='Applicable Job Positions',
        help='Leave empty to apply to all job positions.',
    )
    company_id = fields.Many2one(
        'res.company',
        string='Company',
        default=lambda self: self.env.company,
    )

    @api.constrains('criteria_ids')
    def _check_criteria_weights(self):
        for template in self:
            if template.criteria_ids:
                total_weight = sum(template.criteria_ids.mapped('weight'))
                if abs(total_weight - 100.0) > 0.01:
                    raise ValidationError(
                        _('The total weight of all criteria must equal 100%%. '
                          'Current total: %.1f%%') % total_weight)


class ReviewCriteria(models.Model):
    _name = 'hr.review.criteria'
    _description = 'Review Evaluation Criteria'
    _order = 'sequence, id'

    template_id = fields.Many2one(
        'hr.review.template',
        string='Template',
        required=True,
        ondelete='cascade',
    )
    name = fields.Char(
        string='Criteria Name',
        required=True,
    )
    description = fields.Text(string='Description')
    weight = fields.Float(
        string='Weight (%)',
        required=True,
        default=20.0,
    )
    sequence = fields.Integer(string='Sequence', default=10)
    category = fields.Selection([
        ('performance', 'Job Performance'),
        ('competency', 'Core Competencies'),
        ('behavior', 'Behavioral'),
        ('leadership', 'Leadership'),
        ('teamwork', 'Teamwork'),
        ('communication', 'Communication'),
        ('innovation', 'Innovation'),
        ('other', 'Other'),
    ], string='Category', default='performance', required=True)
