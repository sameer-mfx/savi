from odoo import models, fields, api, _
from odoo.exceptions import UserError

class ServiceOrderLine(models.Model):
    _name = 'service.order.line'
    _description = 'Service Order Line'

    order_id = fields.Many2one(comodel_name='service.order', string='Order', ondelete='cascade')
    product_id = fields.Many2one(comodel_name='product.product', string='Product')
    service_product_id = fields.Many2one(comodel_name='product.product', domain="[('detailed_type', '=', 'service')]", required=True)
    description = fields.Char(string='Description')
    is_tracked = fields.Boolean(string='Tracked', compute='_compute_is_tracked', store=True, default=False)
    product_identification_ids = fields.Many2many(comodel_name='stock.lot', string='Identification Numbers', copy=False)
    quantity = fields.Float(string='Quantity', default=1)
    uom_id = fields.Many2one(comodel_name='uom.uom', string='Unit of Measure')
    unit_price = fields.Float(string='Unit Price')
    company_id = fields.Many2one(comodel_name='res.company', string='Company', required=True, default=lambda self: self.env.user.company_id.id, copy=False)
    tax_ids = fields.Many2many(comodel_name='account.tax', string='Taxes')
    sub_total = fields.Float(string='Total Price', compute="_order_line_calculate_sub_total")
    under_warranty = fields.Boolean(string='Under Warranty')
    location = fields.Char(string='Location')
    remarks = fields.Text(string='Remarks')

    @api.depends('product_id')
    def _compute_is_tracked(self):
        for record in self:
            record.is_tracked = record.product_id.tracking != 'none'

    @api.constrains('quantity', 'unit_price')
    def product_qty_constrains(self):
        for line in self:
            if not line.quantity or line.quantity <= 0:
                raise UserError(
                    _("Quantity must be always positive and greater than zero in line with product %s and service product %s in order %s" % (
                    line.product_id.name, line.service_product_id.name, line.order_id.name)))
            if line.unit_price and line.unit_price < 0:
                raise UserError(
                    _("Price must be always positive and greater than zero in line with product %s and service product %s in order %s" % (
                    line.product_id.name, line.service_product_id.name, line.order_id.name)))

    @api.onchange('product_id', 'service_product_id')
    def _update_description_in_order_lines(self):
        if self.order_id.state in ('approved', 'cancel'):
            raise UserError(_("You are not allowed to create order lines as order is in %s state" % self.order_id.state))
        if self.product_id and self.service_product_id:
            self.unit_price = self.service_product_id.list_price
            self.description = str(self.service_product_id.display_name) + ' ON ' + str(self.product_id.display_name)
            self.uom_id = self.product_id.uom_id

    def _order_line_calculate_sub_total(self):
        for line in self:
            vals = line._prepare_compute_all_values()
            taxes = line.tax_ids.compute_all(
                vals['price_unit'],
                vals['currency_id'],
                vals['product_qty'],
                vals['product'],
                vals['partner']
            )
            line.update({
                'sub_total': taxes['total_included'],
            })

    def _prepare_compute_all_values(self):
        self.ensure_one()
        return {
            'price_unit': self.unit_price,
            'currency_id': self.order_id.currency_id,
            'product_qty': self.quantity,
            'product': self.service_product_id,
            'partner': self.order_id.customer_id,
        }

    @api.model
    def create(self, vals):
        if vals.get('order_id'):
            order = self.env['service.order'].browse(vals['order_id'])
            if order.state != 'draft':
                raise UserError(_("You cannot add more lines in this order %s" % order.name))

            product_id = vals.get('product_id')
            service_product_id = vals.get('service_product_id')

            domain = [('order_id', '=', vals['order_id']), ('product_id', '=', product_id), ('service_product_id', '=', service_product_id)]

            grouped = self.env['service.order.line'].read_group(domain, ['product_id', 'service_product_id'], ['product_id', 'service_product_id'])

            if grouped and grouped[0]['product_id_count'] > 0:
                prod = self.env['product.product'].browse(product_id).name
                service_prod = self.env['product.product'].browse(service_product_id).name
                raise UserError(
                    _("Please don't create duplicate order lines with product %s and service product %s in %s" % (
                    prod, service_prod, order.name)))
        return super(ServiceOrderLine, self).create(vals)

    def write(self, vals):
        if self.order_id.state not in ('draft', 'to_approve'):
            raise UserError(_("You are not allowed to change anything in this order %s as it is not in draft state" %(self.order_id.name)))
        return super(ServiceOrderLine, self).write(vals)

    def unlink(self):
        for line in self:
            if line.order_id.state != 'draft':
                raise UserError(_("You are not allowed to delete line from this SSO %s as it is not in draft state" %line.order_id.name))
        return super(ServiceOrderLine, self).unlink()