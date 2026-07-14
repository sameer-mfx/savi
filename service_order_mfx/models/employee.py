from odoo import api, fields, models, _

class Employee(models.Model):
    _inherit = 'hr.employee'

    performance_rating = fields.Float(string="Performance Rating", compute='_compute_performance_rating')

    def _compute_performance_rating(self):
        Srn = self.env['srn']
        for employee in self:
            if not employee.user_id:
                employee.performance_rating = 0
                continue
            srns = Srn.search([('user_id', '=', employee.user_id.id), ('state', '=', 'done')])
            employee.performance_rating = (
                sum(int(srn.performance_rating or 0) for srn in srns) / len(srns)
                if srns else 0
            )
