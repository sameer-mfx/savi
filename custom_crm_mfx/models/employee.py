from odoo import fields, models

class HrEmployee(models.Model):
    _inherit = 'hr.employee'

    manager_ids = fields.Many2many(
        comodel_name='hr.employee',
        relation='employee_manager_rel',
        column1='employee_id',
        column2='manager_id',
        string='Additional Managers'
    )