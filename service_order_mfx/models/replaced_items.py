from odoo import api, fields, models, _
from odoo.exceptions import UserError

class ReplacedItems(models.Model):
    _name = "replaced.items"
    _description = "Replaced Items"

    # **============== Fields ==============**

    srn_line_id = fields.Many2one(comodel_name='srn.line', required=True, ondelete='cascade')
    srn_id = fields.Many2one(comodel_name='srn', required=True, ondelete='cascade')
    service_order_id = fields.Many2one(comodel_name='service.order', required=True, ondelete='cascade')
    product_id = fields.Many2one(comodel_name='product.product', string='Replaced Product', required=True, ondelete='cascade')
    product_uom_id = fields.Many2one(comodel_name='uom.uom', related='product_id.uom_id', ondelete='cascade')
    quantity = fields.Float(string='Quantity', required=True, digits='Product Unit of Measure', default=1)
    price = fields.Float(string='Unit Price')
    tax_ids = fields.Many2many('account.tax')
    price_subtotal = fields.Float(string='Sub Total', compute="_replaced_items_compute_sub_total")

    # **============== Methods ==============**

    @api.constrains('price', 'quantity')
    def replaced_items_check_price_and_quantity(self):
        for ri in self:
            if not ri.price or ri.price <= 0 and not ri.srn_line_id.service_order_line_id.under_warranty:
                raise UserError(_("Price must be greater than zero for replaced items with product %s in %s as it is not under warranty." %(ri.product_id.name, ri.srn_id.name)))
            if not ri.quantity or ri.quantity <= 0:
                raise UserError(_("Quantity must be greater than zero for replaced items with product %s in %s" %(ri.product_id.name, ri.srn_id.name)))

    def _replaced_items_compute_sub_total(self):
        for item in self:
            vals = item._prepare_compute_all_values_replaced_items()
            taxes = item.tax_ids.compute_all(
                vals['price_unit'],
                vals['currency_id'],
                vals['product_qty'],
                vals['product'],
                vals['partner']
            )
            item.update({
                'price_subtotal': taxes['total_included'],
            })

    def _prepare_compute_all_values_replaced_items(self):
        self.ensure_one()
        return {
            'price_unit': self.price,
            'currency_id': self.srn_id.customer_id.currency_id,
            'product_qty': self.quantity,
            'product': self.product_id,
            'partner': self.srn_id.customer_id,
        }

    @api.model
    def create(self, vals):
        existing_replaced_items = self.env['replaced.items'].search([('srn_line_id', '=', vals.get('srn_line_id'))])
        if vals.get('product_id') in existing_replaced_items.mapped('product_id').ids:
            product = self.env['product.product'].browse(vals['product_id']).name
            srn = self.env['srn.line'].browse(vals['srn_line_id']).srn_id.name
            raise UserError(_("A replaced item line has already been created with same product %s in SRN %s" %(product, srn)))
        if not vals.get('quantity') or vals.get('quantity') <= 0:
            product = self.env['product.product'].browse(vals['product_id']).name
            srn = self.env['srn.line'].browse(vals['srn_line_id']).srn_id.name
            raise UserError(_("Quantity must be grater than zero for replaced item with product %s in SRN %s" %(product, srn)))
        # if not vals.get('price'):
        #     product = self.env['product.product'].browse(vals['product_id']).name
        #     srn = self.env['srn.line'].browse(vals['srn_line_id']).srn_id.name
        #     raise UserError(_("Price must be greater than zero for replaced items with product %s in %s" %(product, srn)))
        return super(ReplacedItems, self).create(vals)

class Srn(models.Model):
    _inherit = 'srn'

    # **============== Fields ==============**

    replaced_item_ids = fields.One2many('replaced.items', 'srn_id')

class SrnLine(models.Model):
    _inherit = 'srn.line'

    # **============== Fields ==============**

    replaced_item_ids = fields.One2many('replaced.items', 'srn_line_id')

    # **============== Methods ==============**

    def srn_line_show_replaced_items(self):
        if not self.product_qty:
            raise UserError(_("You are not allowed to add replaced items for this line as the Product Qty is zero in SRN %s." %self.srn_id.name))
        view = self.env.ref('service_order_mfx.replaced_items_form_view')
        spo_id = self.env['service.order']
        if self.service_order_line_id:
            spo_id = self.service_order_line_id.order_id
        return {
            'name': _('Replaced Items'),
            'type': 'ir.actions.act_window',
            'view_type': 'form',
            'view_mode': 'form',
            'res_model': 'srn.line',
            'views': [(view.id, 'form')],
            'view_id': view.id,
            'target': 'new',
            'res_id': self.id,
            'context': {'default_product_id':self.product_id.id,'default_service_product_id':self.service_product_id.id,'default_srn_line_id':self.id,'default_srn_id':self.srn_id.id,'default_service_order_id':spo_id.id}
        }