from odoo import models, fields, api, _
from datetime import timedelta


class SaleOrderLine(models.Model):
    _inherit = 'sale.order.line'

    margin_percentage = fields.Float(string='Margin (%)')

    @api.onchange('margin_percentage')
    def _onchange_margin_percentage(self):
        for line in self:
            if line.purchase_price and line.margin_percentage:
                line.price_unit = line.purchase_price * (1 + line.margin_percentage / 100)
            elif line.purchase_price and not line.margin_percentage:
                line.price_unit = line.purchase_price

    @api.onchange('product_id')
    def _onchange_product_id_price_warning(self):
        if not self.product_id:
            return
        template = self.product_id.product_tmpl_id
        last_cost_update = template.last_cost_update
        today = fields.Date.today()
        threshold = today - timedelta(days=30)

        if not last_cost_update or last_cost_update < threshold:
            if last_cost_update:
                days_ago = (today - last_cost_update).days
                message = _(
                    "The cost price for '%s' was last updated %d days ago. "
                    "Please verify the cost with OEM before proceeding.",
                    template.name, days_ago,
                )
            else:
                message = _(
                    "No cost price update date found for '%s'. "
                    "Please verify the cost with OEM before proceeding.",
                    template.name,
                )
            return {
                'warning': {
                    'title': _('Cost Price Review Required'),
                    'message': message,
                }
            }
