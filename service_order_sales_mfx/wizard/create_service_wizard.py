from odoo import models, fields, api, _
from odoo.exceptions import UserError

class CreateServiceOrderLineWizard(models.TransientModel):
    _name = 'create.service.order.line.wizard'
    _description = 'Wizard Line for Service Order Creation'

    wizard_id = fields.Many2one(comodel_name='create.service.order.wizard', string="Wizard")
    product_id = fields.Many2one(comodel_name='product.product', string="Product", readonly=True)
    sale_order_line_id = fields.Many2one(comodel_name='sale.order.line', string="Sale Order Line", readonly=True)
    service_product_id = fields.Many2one(comodel_name='product.product', string="Service Product", domain=[('detailed_type', '=', 'service')])
    product_qty = fields.Float(string="Quantity")

    @api.onchange('product_qty')
    def _onchange_product_qty(self):
        if self.product_qty > self.sale_order_line_id.product_uom_qty:
            raise UserError(_("Quantity must be less than or equal to the quantity in the sale order line."))

class CreateServiceOrderWizard(models.TransientModel):
    _name = 'create.service.order.wizard'
    _description = 'Create Service Order Wizard'

    sale_order_id = fields.Many2one(comodel_name='sale.order', string="Sale Order", readonly=True)
    line_ids = fields.One2many(comodel_name='create.service.order.line.wizard', inverse_name='wizard_id', string="Lines")

    def action_create_service_order(self):
        lines = []
        for wizard_line in self.line_ids:
            if not wizard_line.service_product_id or not wizard_line.product_qty:
                continue
            vals = {
                'product_id': wizard_line.product_id.id,
                'service_product_id': wizard_line.service_product_id.id,
                'description': wizard_line.service_product_id.name + ' ON ' + wizard_line.product_id.name,
                'uom_id': wizard_line.product_id.uom_id.id,
                'unit_price': 0.0 if wizard_line.sale_order_line_id.warranty_end_date <= fields.Date.today() else wizard_line.service_product_id.list_price,
                'under_warranty': wizard_line.sale_order_line_id.warranty_end_date > fields.Date.today(),
                'quantity': wizard_line.product_qty,
            }
            lines.append((0, 0, vals))
        if not lines:
            raise UserError(_("Please select both service product and quantity in atleast one line to create service order."))
        vals = {
            'customer_id': self.sale_order_id.partner_id.id,
            'user_id': self.sale_order_id.user_id.id,
            'date_order': fields.Datetime.now(),
            'company_id': self.sale_order_id.company_id.id,
            'state': 'draft',
            'origin': self.sale_order_id.name,
            'order_line_ids': lines
        }
        service_order = self.env['service.order'].create(vals)
        self.sale_order_id.service_order_ids |= service_order