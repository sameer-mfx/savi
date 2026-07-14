from odoo import api, fields, models, _
from odoo.exceptions import UserError

class ProductSupplierinfo(models.Model):
    _inherit = 'product.supplierinfo'

    payment_terms = fields.Many2one('account.payment.term', string='Payment Terms')
    freight_cost = fields.Char(string='Freight Cost')
    margin = fields.Float(string='Margin (%)')
    multi_brands = fields.Many2many(comodel_name='product.make')
    categories = fields.Many2one(comodel_name='product.category')

class ProductTemplate(models.Model):
    _inherit = 'product.template'

    warranty_period = fields.Integer(string='Warranty Period')
    warranty_type = fields.Selection([('month', 'Months'), ('year', 'Years')])
    margin = fields.Float(string='Margin (%)')

    @api.onchange('margin', 'standard_price')
    def _onchange_margin(self):
        if self.margin:
            self.list_price = self.standard_price * (1 + self.margin / 100)

    @api.onchange('default_code')
    def _onchange_default_codes(self):
        if not self.default_code:
            return

        domain = [('default_code', 'in', (self.default_code.upper(), self.default_code.lower()))]
        if self.id.origin:
            domain.append(('id', '!=', self.id.origin))

        if self.env['product.template'].search(domain, limit=1):
            raise UserError(_("Default Code must be unique"))

class ProductProduct(models.Model):
    _inherit = 'product.product'

    @api.onchange('default_code')
    def _onchange_default_codes(self):
        if not self.default_code:
            return

        domain = [('default_code', 'in', (self.default_code.upper(), self.default_code.lower()))]
        if self.id.origin:
            domain.append(('id', '!=', self.id.origin))

        if self.env['product.product'].search(domain, limit=1):
            raise UserError(_("Default Code must be unique"))