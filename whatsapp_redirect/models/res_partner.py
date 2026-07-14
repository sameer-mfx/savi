from odoo import models, _

class ResPartner(models.Model):
    """Extends the res_partner model to add a new action for sending WhatsApp
    messages."""
    _inherit = 'res.partner'

    def action_send_msg(self):
        """This function is called when the user clicks the
         'Send WhatsApp Message' button on a partner's form view. It opens a
          new wizard to compose and send a WhatsApp message."""
        return {'type': 'ir.actions.act_window',
                'name': _('Whatsapp Message'),
                'res_model': 'whatsapp.send.message',
                'target': 'new',
                'view_mode': 'form',
                'view_type': 'form',
                'context': {'default_user_id': self.id}, }