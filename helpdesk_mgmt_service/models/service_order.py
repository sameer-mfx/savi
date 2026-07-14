from odoo import api, fields, models

class ServiceOrder(models.Model):
    _inherit = "service.order"

    ticket_ids = fields.Many2many("helpdesk.ticket")
    ticket_count = fields.Integer(
        string="Tickets Count", compute="_compute_ticket_count", store=True
    )

    @api.depends("ticket_ids")
    def _compute_ticket_count(self):
        for order in self:
            order.ticket_count = len(order.ticket_ids)