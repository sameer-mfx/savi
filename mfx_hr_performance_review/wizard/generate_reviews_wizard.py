from odoo import api, fields, models, _
from odoo.exceptions import UserError


class GenerateReviewsWizard(models.TransientModel):
    _name = 'hr.generate.reviews.wizard'
    _description = 'Generate Performance Reviews Wizard'

    cycle_id = fields.Many2one(
        'hr.review.cycle',
        string='Review Cycle',
        required=True,
    )
    department_ids = fields.Many2many(
        'hr.department',
        string='Departments',
        help='Leave empty to generate for all departments.',
    )
    employee_ids = fields.Many2many(
        'hr.employee',
        string='Specific Employees',
        help='Leave empty to generate for all employees in selected departments.',
    )
    skip_existing = fields.Boolean(
        string='Skip Existing Reviews',
        default=True,
        help='If checked, employees who already have a review in this cycle will be skipped.',
    )

    @api.onchange('cycle_id')
    def _onchange_cycle_id(self):
        if self.cycle_id and self.cycle_id.department_ids:
            self.department_ids = self.cycle_id.department_ids

    def action_generate(self):
        self.ensure_one()
        cycle = self.cycle_id

        # Determine employees
        domain = [
            ('active', '=', True),
            ('employee_type', '=', 'employee'),
        ]
        if self.employee_ids:
            domain.append(('id', 'in', self.employee_ids.ids))
        elif self.department_ids:
            domain.append(('department_id', 'in', self.department_ids.ids))
        elif cycle.department_ids:
            domain.append(('department_id', 'in', cycle.department_ids.ids))

        employees = self.env['hr.employee'].search(domain)

        if not employees:
            raise UserError(_('No employees found matching the criteria.'))

        # Skip existing
        existing_employee_ids = []
        if self.skip_existing:
            existing = self.env['hr.performance.review'].search([
                ('cycle_id', '=', cycle.id),
            ])
            existing_employee_ids = existing.mapped('employee_id').ids

        created_count = 0
        skipped_count = 0
        review_vals_list = []

        for employee in employees:
            if employee.id in existing_employee_ids:
                skipped_count += 1
                continue

            review_vals_list.append({
                'employee_id': employee.id,
                'manager_id': employee.parent_id.id if employee.parent_id else False,
                'cycle_id': cycle.id,
                'date_review': cycle.date_end,
                'company_id': employee.company_id.id,
            })
            created_count += 1

        if review_vals_list:
            self.env['hr.performance.review'].create(review_vals_list)

        message = _('%d review(s) created successfully.') % created_count
        if skipped_count:
            message += _(' %d employee(s) skipped (already have reviews).') % skipped_count

        return {
            'type': 'ir.actions.client',
            'tag': 'display_notification',
            'params': {
                'title': _('Reviews Generated'),
                'message': message,
                'type': 'success',
                'sticky': False,
                'next': {
                    'type': 'ir.actions.act_window',
                    'name': _('Performance Reviews'),
                    'res_model': 'hr.performance.review',
                    'view_mode': 'tree,form,kanban',
                    'domain': [('cycle_id', '=', cycle.id)],
                    'views': [
                        (False, 'tree'),
                        (False, 'form'),
                        (False, 'kanban'),
                    ],
                },
            },
        }
