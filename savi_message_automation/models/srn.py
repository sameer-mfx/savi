from odoo import fields, models

from .message_utils import savi_param_bool


class Srn(models.Model):
    _inherit = "srn"

    def write(self, vals):
        result = super().write(vals)
        if vals.get("state") == "done":
            self._savi_send_srn_feedback_email()
        return result

    def srn_button_approve(self):
        result = super().srn_button_approve()
        self._savi_send_srn_feedback_email()
        return result

    def _savi_send_srn_feedback_email(self):
        if not savi_param_bool(self.env, "srn_feedback_email_enabled"):
            return
        template = self.env.ref(
            "service_order_mfx.email_template_srn_satisfaction",
            raise_if_not_found=False,
        )
        if not template:
            return
        for srn in self:
            if srn.state != "done" or srn.satisfaction_email_sent or not srn.customer_id.email:
                continue
            template.send_mail(srn.id, force_send=True)
            srn.write({
                "satisfaction_email_sent": True,
                "satisfaction_email_sent_date": fields.Datetime.now(),
                "satisfaction_email_sent_by": self.env.user.id,
            })
