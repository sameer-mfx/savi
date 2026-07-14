from odoo import api, fields, models


class SaleOrder(models.Model):
    _inherit = "sale.order"

    def _savi_get_default_reminder_days(self):
        value = self.env["ir.config_parameter"].sudo().get_param(
            "savi_phase2_workflow_config.default_quotation_reminder_days",
            "3",
        )
        try:
            days = int(value)
        except (TypeError, ValueError):
            days = 3
        return days if days > 0 else 0

    def _savi_apply_default_quotation_reminder(self):
        default_days = self._savi_get_default_reminder_days()
        if not default_days:
            return
        today = fields.Date.today()
        for order in self:
            if order.state == "sent" and not order.remind_every:
                vals = {"remind_every": default_days}
                if not order.quotation_sent_date:
                    vals["quotation_sent_date"] = today
                order.write(vals)

    @api.model_create_multi
    def create(self, vals_list):
        orders = super().create(vals_list)
        orders._savi_apply_default_quotation_reminder()
        return orders

    def write(self, vals):
        result = super().write(vals)
        if vals.get("state") == "sent" or "remind_every" in vals:
            self._savi_apply_default_quotation_reminder()
        return result
