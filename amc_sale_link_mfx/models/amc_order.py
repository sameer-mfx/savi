from odoo import models, fields, _
from odoo.exceptions import UserError

class AmcOrder(models.Model):
    _inherit = "amc.order"

    sale_order_id = fields.Many2one(comodel_name='sale.order', string="Quotations")

    def action_create_quotation(self):
        if any(amc.state == 'expired' for amc in self):
            raise UserError(_("Cannot create a quotation against an expired AMC Order."))
        SaleOrder = self.env['sale.order']
        SaleOrderLine = self.env['sale.order.line']

        for amc in self:
            amc_period_text = ''
            if amc.amc_start_date and amc.amc_end_date:
                amc_period_text = "AMC Period: %s to %s" % (
                    amc.amc_start_date.strftime('%d %b %Y'),
                    amc.amc_end_date.strftime('%d %b %Y'),
                )

            so_vals = {
                'partner_id': amc.partner_id.id,
                'origin': f"AMC-{amc.id}",
                'amc_id': amc.id,
                'email': amc.partner_id.email or '',
                'mobile': amc.partner_id.mobile or '',
                'amc_end_date': amc.amc_end_date or False,
            }

            sale_order = SaleOrder.create(so_vals)
            amc.sale_order_id = sale_order.id

            for line in amc.amc_lines_ids:
                description = line.product_id.display_name
                if line.product_identification_ids:
                    extra_desc = ", ".join(line.product_identification_ids.mapped('name'))
                    description += f"\n({extra_desc})"
                if amc_period_text:
                    description += f"\n{amc_period_text}"
                SaleOrderLine.create({
                    'order_id': sale_order.id,
                    'product_id': line.product_id.id,
                    'name': description,
                    'product_uom_qty': line.quantity,
                    'price_unit': line.unit_price,
                    'tax_id': line.tax_ids.ids,
                })

        return {
            'type': 'ir.actions.act_window',
            'res_model': 'sale.order',
            'view_mode': 'form',
            'res_id': sale_order.id,
        }

class SaleOrder(models.Model):
    _inherit = "sale.order"

    amc_id = fields.Many2one(comodel_name='amc.order', string="AMC Order")
    amc_end_date = fields.Date(string="AMC End Date")

    def action_open_amc_order(self):
        self.ensure_one()
        return {
            'type': 'ir.actions.act_window',
            'res_model': 'amc.order',
            'view_mode': 'form',
            'res_id': self.amc_id.id,
        }

    def action_confirm(self):
        for order in self:
            if order.amc_id:
                order.state = 'sale'
            else:
                super(SaleOrder, order).action_confirm()
        return True