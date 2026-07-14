from odoo import api, fields, models

class ConstructionTaskLines(models.Model):
    _inherit = 'cons.task.line'

    margin_percentage = fields.Float(string='Margin Percentage')
    model = fields.Many2one('product.make')
    serial_no = fields.Char(string='Serial Number')
    warranty_start_date = fields.Date(string='Warranty Start Date')
    warranty_end_date = fields.Date(string='Warranty End Date')
    remind_before = fields.Integer()

    @api.onchange('margin_percentage')
    def compute_margin_percentage(self):
        if self.margin_percentage and self.original_unit_cost:
            self.original_unit_price = self.original_unit_cost + (self.original_unit_cost * (self.margin_percentage / 100))