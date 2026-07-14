from odoo import api, fields, models, _

class Employee(models.Model):
    _inherit = 'hr.employee'

    performance_rating = fields.Float(string="Performance Rating", compute='_compute_performance_rating')

    def _compute_performance_rating(self):
        srns = self.env['srn'].search([('user_id', '=', self.user_id.id), ('state', '=', 'done')])
        average_srn_rating = sum(int(srn.performance_rating) for srn in srns) / len(srns) if srns else 0
        self.performance_rating = average_srn_rating