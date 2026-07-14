from odoo import api, fields, models

from .message_utils import savi_param_bool


class CrmLead(models.Model):
    _inherit = "crm.lead"

    savi_enquiry_ack_sent = fields.Boolean(string="SAVI Enquiry Ack Sent", copy=False, readonly=True)
    savi_enquiry_ack_sent_date = fields.Datetime(string="SAVI Enquiry Ack Sent On", copy=False, readonly=True)

    @api.model_create_multi
    def create(self, vals_list):
        leads = super().create(vals_list)
        leads._savi_send_enquiry_acknowledgement()
        return leads

    def _savi_send_enquiry_acknowledgement(self):
        if not savi_param_bool(self.env, "lead_ack_email_enabled"):
            return
        template = self.env.ref(
            "savi_message_automation.email_template_lead_acknowledgement",
            raise_if_not_found=False,
        )
        if not template:
            return
        for lead in self:
            email_to = lead.email_from or lead.partner_id.email
            if lead.savi_enquiry_ack_sent or not email_to:
                continue
            template.send_mail(lead.id, force_send=True)
            lead.write({
                "savi_enquiry_ack_sent": True,
                "savi_enquiry_ack_sent_date": fields.Datetime.now(),
            })
