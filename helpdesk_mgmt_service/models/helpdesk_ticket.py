from odoo import api, fields, models

class HelpdeskTicket(models.Model):
    _inherit = "helpdesk.ticket"

    service_order_ids = fields.Many2many("service.order")
    sso_count = fields.Integer(
        string="Service Order Count", compute="_compute_sso_count", store=True
    )

    @api.depends("service_order_ids")
    def _compute_sso_count(self):
        for ticket in self:
            ticket.sso_count = len(ticket.service_order_ids)

    def action_view_service_orders(self):
        """Returns action to view sale orders related to this ticket."""
        action = self.env["ir.actions.actions"]._for_xml_id("service_order_mfx.action_service_quotation")
        action["domain"] = [("ticket_ids", "in", [self.id])]
        action["context"] = {
            "default_ticket_ids": [(4, [self.id])],
            "default_customer_id": self.partner_id.id,
            "default_user_id": self.user_id.id,
        }
        return action