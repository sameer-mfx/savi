from odoo import models, fields, api

class AmcServices(models.Model):
    _name = 'amc.services'
    _description = 'AMC Services'

    product_id = fields.Many2one(comodel_name='product.product', string='Product', required=True)
    name = fields.Char(string='Service Name', required=True)
    description = fields.Text(string='Description', required=True)
    company_id = fields.Many2one(comodel_name='res.company', string='Company', default=lambda self: self.env.user.company_id.id)