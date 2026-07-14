from odoo import fields, models

from .message_utils import savi_param_bool


class StockPicking(models.Model):
    _inherit = "stock.picking"

    savi_dispatch_update_sent = fields.Boolean(string="SAVI Dispatch Update Sent", copy=False, readonly=True)
    savi_dispatch_update_sent_date = fields.Datetime(string="SAVI Dispatch Update Sent On", copy=False, readonly=True)

    def write(self, vals):
        result = super().write(vals)
        if vals.get("state") == "done":
            self._savi_send_dispatch_update()
        return result

    def _savi_send_dispatch_update(self):
        if not savi_param_bool(self.env, "dispatch_customer_email_enabled"):
            return
        template = self.env.ref(
            "savi_message_automation.email_template_dispatch_update",
            raise_if_not_found=False,
        )
        if not template:
            return
        for picking in self:
            if (
                picking.savi_dispatch_update_sent
                or picking.state != "done"
                or picking.picking_type_code != "outgoing"
                or not picking.partner_id.email
            ):
                continue
            template.send_mail(picking.id, force_send=True)
            picking.write({
                "savi_dispatch_update_sent": True,
                "savi_dispatch_update_sent_date": fields.Datetime.now(),
            })
