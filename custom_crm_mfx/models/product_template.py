from odoo import models, fields, api, _


# Map each price field to its corresponding last-update date field
PRICE_DATE_MAP = {
    'list_price': 'last_salesprice_update',
    'standard_price': 'last_cost_update',
}


class ProductTemplate(models.Model):
    _inherit = 'product.template'

    make = fields.Many2one(comodel_name='product.make', string='Make')
    website_url = fields.Char(string='Url')
    maximum_retail_price = fields.Float(
        string='Maximum Retail Price',
        tracking=True,
        digits='Product Price',
    )
    last_cost_update = fields.Date(
        string='Last Cost Update',
        help='Date when the Cost (standard_price) was last changed.',
    )
    last_salesprice_update = fields.Date(
        string='Last Sales Price Update',
        help='Date when the Sales Price (list_price) was last changed.',
    )

    @api.model_create_multi
    def create(self, vals_list):
        today = fields.Date.today()
        for vals in vals_list:
            for price_field, date_field in PRICE_DATE_MAP.items():
                if price_field in vals:
                    vals[date_field] = today
        return super().create(vals_list)

    def write(self, vals):
        res = super().write(vals)
        today = fields.Date.today()
        date_updates = {}
        for price_field, date_field in PRICE_DATE_MAP.items():
            if price_field in vals:
                date_updates[date_field] = today
        if date_updates:
            super(ProductTemplate, self).write(date_updates)
        return res


class ProductMake(models.Model):
    _name = 'product.make'

    name = fields.Char(string='Name')
