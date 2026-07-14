from odoo import api, fields, models
from odoo.exceptions import UserError

class HelpdeskTicket(models.Model):
    _inherit = "helpdesk.ticket"

    product_id = fields.Many2one(comodel_name="product.product", string="Product")
    product_identification_id = fields.Many2one(comodel_name="stock.lot", string="Product Identification")
    amc_id = fields.Many2one(comodel_name="amc.order", string="AMC")
    amc_validity = fields.Selection(selection=[('na', 'AMC not found'), ('valid', 'Valid'), ('invalid', 'Invalid'), ('expired', 'Expired')], default='na')

    def fetch_amc(self):
        for ticket in self:
            if not ticket.product_id and not ticket.product_identification_id:
                raise UserError("Please select a Product or Product Identification before fetching AMC.")
            if not ticket.partner_id:
                raise UserError("Please select a partner before fetching AMC.")

            product = ticket.product_id or ticket.product_identification_id.product_id

            partner_ids = [ticket.partner_id.id]
            if ticket.partner_id.is_company:
                child_partners = self.env['res.partner'].search([('parent_id', '=', ticket.partner_id.id)])
                partner_ids += child_partners.ids
            else:
                if ticket.partner_id.parent_id:
                    partner_ids.append(ticket.partner_id.parent_id.id)

            # Build domain
            domain = [
                ('amc_id.partner_id', 'in', partner_ids),
                ('product_id', '=', product.id)
            ]

            # Filter by selected product_identification_id if provided
            if ticket.product_identification_id:
                domain.append(('product_identification_ids', 'in', ticket.product_identification_id.ids))

            amc_lines = self.env['amc.order.lines'].search(domain, order="id desc", limit=5)
            if not amc_lines:
                ticket.amc_validity = 'na'
                ticket.amc_id = False
                continue

            # Prioritize AMCs by their state
            valid_amc = amc_lines.filtered(lambda l: l.amc_id.state == 'approved')
            invalid_amc = amc_lines.filtered(lambda l: l.amc_id.state in ('draft', 'to_approve'))
            expired_amc = amc_lines.filtered(lambda l: l.amc_id.state == 'expired')

            if valid_amc:
                ticket.amc_id = valid_amc[0].amc_id.id
                ticket.amc_validity = 'valid'
            elif invalid_amc:
                ticket.amc_id = invalid_amc[0].amc_id.id
                ticket.amc_validity = 'invalid'
            elif expired_amc:
                # ✅ Show expired AMC instead of clearing it
                ticket.amc_id = expired_amc[0].amc_id.id
                ticket.amc_validity = 'expired'
            else:
                ticket.amc_validity = 'na'
                ticket.amc_id = False