from odoo import fields, models

class WhatsappSendMessage(models.TransientModel):
    """This model is used for sending WhatsApp messages through Odoo."""
    _name = 'whatsapp.send.message'
    _description = "Whatsapp Wizard"

    user_id = fields.Many2one('res.partner', string="Recipient")
    mobile = fields.Char(related='user_id.mobile', required=True)
    message = fields.Text(string="Message", required=True)

    def action_send_message(self):
        """This method is called to send the WhatsApp message using the
         provided details."""
        if self.message and self.mobile:
            message = self.message.replace(' ', '%20').replace('\n', '%0A')
            return {
                'type': 'ir.actions.act_url',
                'url': "https://api.whatsapp.com/send?phone=" +
                       self.user_id.mobile + "&text=" + message,
                'target': 'new',
                'res_id': self.id,
            }