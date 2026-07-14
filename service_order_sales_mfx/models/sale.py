from odoo import models, fields, api, _
from odoo.exceptions import UserError

class SaleOrder(models.Model):
    _inherit = 'sale.order'

    service_order_ids = fields.Many2many(comodel_name='service.order', string="Service Orders")
    sso_count = fields.Integer(string="Service Orders", compute='_compute_sso_count')

    def button_show_service_orders(self):
        self.ensure_one()
        return {
            'name': 'Service Orders',
            'type': 'ir.actions.act_window',
            'res_model': 'service.order',
            'view_mode': 'tree,form',
            'domain': [('id', 'in', self.service_order_ids.ids)],
        }

    @api.depends('service_order_ids')
    def _compute_sso_count(self):
        self.sso_count = len(self.service_order_ids)

    def create_service_order(self):
        view_id = self.env.ref('service_order_sales_mfx.view_create_service_order_wizard_form').id
        self.ensure_one()
        wizard = self.env['create.service.order.wizard'].create({
            'sale_order_id': self.id,
            'line_ids': [
                (0, 0, {
                    'product_id': line.product_id.id,
                    'sale_order_line_id': line.id,
                    'product_qty': line.product_uom_qty,
                }) for line in self.order_line.filtered(lambda l: l.product_id)
            ],
        })
        return {
            'name': 'Create Service Order',
            'type': 'ir.actions.act_window',
            'res_model': 'create.service.order.wizard',
            'view_mode': 'form',
            'view_id': view_id,
            'res_id': wizard.id,
            'target': 'new',
        }