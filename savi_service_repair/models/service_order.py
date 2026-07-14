from odoo import fields, models


class ServiceOrder(models.Model):
    _inherit = "service.order"

    savi_repair_ids = fields.One2many("x_savi.service.repair", "service_order_id", string="Repair Cases")
    savi_repair_count = fields.Integer(compute="_compute_savi_repair_count")

    def _compute_savi_repair_count(self):
        for order in self:
            order.savi_repair_count = len(order.savi_repair_ids)

    def action_view_savi_repairs(self):
        self.ensure_one()
        action = self.env.ref("savi_service_repair.action_x_savi_service_repair").read()[0]
        action["domain"] = [("service_order_id", "=", self.id)]
        action["context"] = {
            "default_service_order_id": self.id,
            "default_customer_id": self.customer_id.id,
            "default_customer_ref": self.customer_ref,
            "default_assigned_to": self.assigned_to.id,
        }
        return action
