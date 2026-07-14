from odoo import models, api, fields, _


class AmcLotDetails(models.Model):
    _name = "amc.lot.details"
    _description = "AMC Lot Details"

    lot_id = fields.Many2one(comodel_name='stock.lot', string='Lot/Serial Number')
    product_id = fields.Many2one(comodel_name='product.product', string='Product')
    amc_id = fields.Many2one(comodel_name='amc.order', string='AMC Order')
    partner_id = fields.Many2one(related='amc_id.partner_id', string='Customer', store=True)
    amc_state = fields.Selection(related='amc_id.state', string='AMC Status', store=True)

    def write(self, vals):
        if 'lot_id' in vals:
            for rec in self:
                old_lot_id = rec.lot_id.id
                new_lot_id = vals['lot_id']
                if old_lot_id and new_lot_id and old_lot_id != new_lot_id:
                    # Sync change back to AMC order line's product_identification_ids
                    amc_line = self.env['amc.order.lines'].search([
                        ('amc_id', '=', rec.amc_id.id),
                        ('product_id', '=', rec.product_id.id),
                        ('product_identification_ids', 'in', [old_lot_id]),
                    ], limit=1)
                    if amc_line:
                        amc_line.sudo().write({
                            'product_identification_ids': [(3, old_lot_id), (4, new_lot_id)]
                        })
        return super().write(vals)


class AmcOrder(models.Model):
    _inherit = "amc.order"

    def action_approve_amc(self):
        res = super(AmcOrder, self).action_approve_amc()
        for line in self.amc_lines_ids:
            if line.product_identification_ids:
                for identification in line.product_identification_ids:
                    if identification.id:
                        self.env['amc.lot.details'].create({
                            'lot_id': identification.id,
                            'product_id': line.product_id.id,
                            'amc_id': self.id,
                        })
        return res
