from odoo import models, fields

class ServiceOrder(models.Model):
    _inherit = 'service.order'

    sale_order_id = fields.Many2one('sale.order', ondelete='cascade')
    origin = fields.Char('Source Document')