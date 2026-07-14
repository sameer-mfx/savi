from odoo import models, api, fields, _
from odoo.exceptions import UserError

class Srn(models.Model):
    _inherit = 'srn'

    def send_whatsapp_msg(self):
        self.ensure_one()
        if not self.user_id.partner_id.mobile:
            raise UserError(_("Mobile number is not available for %s." % self.user_id.partner_id.name))

        return {
            'type': 'ir.actions.act_window',
            'name': _('Whatsapp Message'),
            'res_model': 'whatsapp.send.message',
            'target': 'new',
            'view_mode': 'form',
            'context': {'default_user_id': self.user_id.partner_id.id, 'default_srn_id': self.id},
        }

class WhatsappSendMessageSrn(models.TransientModel):
    _inherit = 'whatsapp.send.message'

    srn_id = fields.Many2one(comodel_name='srn', string='SRN', readonly=True)

    @api.onchange('user_id', 'srn_id')
    def _onchange_user_and_srn_id(self):
        if self.user_id and self.env.context.get('send_srn_in_whatsapp'):
            template = self.env['ir.config_parameter'].sudo().get_param('whatsapp.srn_template')
            if template:
                # Convert UTC deadline to user's timezone
                deadline_user_tz = fields.Datetime.context_timestamp(self, self.srn_id.deadline)
                self.message = template.format(
                    engineer_name=self.user_id.name,
                    order_name=self.srn_id.name,
                    deadline=deadline_user_tz.strftime('%d-%b-%Y %H:%M:%S'),
                    assignee_name=self.srn_id.assigned_by.name,
                    user_name=self.env.user.name
                )