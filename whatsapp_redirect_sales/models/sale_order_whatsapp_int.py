from odoo import models, api, fields, _

class SaleOrder(models.Model):
    _inherit = 'sale.order'

    def action_send_quotation_whatsapp(self):
        self.ensure_one()

        return {
            'type': 'ir.actions.act_window',
            'name': _('Whatsapp Message'),
            'res_model': 'whatsapp.send.message',
            'target': 'new',
            'view_mode': 'form',
            'context': {'default_user_id': self.partner_id.id, 'default_sale_order_id': self.id},
        }

class WhatsappSendMessage(models.TransientModel):
    _inherit = 'whatsapp.send.message'

    sale_order_id = fields.Many2one('sale.order', string='Sale Order', readonly=True)

    @api.onchange('user_id', 'sale_order_id')
    def _onchange_user_id(self):
        """Auto-generate message when recipient is changed."""
        if self.user_id and self.env.context.get('send_sale_reminder_whatsapp'):
            template = self.env['ir.config_parameter'].sudo().get_param('whatsapp.sale_reminder_template')
            if template:
                self.message = template.format(
                    partner_name=self.user_id.name,
                    order_name=self.sale_order_id.name,
                    user_name=self.env.user.name,
                    company_name=self.env.user.company_id.name
                )