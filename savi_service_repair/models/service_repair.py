from odoo import api, fields, models, _


class ServiceRepair(models.Model):
    _name = "x_savi.service.repair"
    _description = "SAVI Service Repair Case"
    _inherit = ["mail.thread", "mail.activity.mixin"]
    _order = "id desc"

    name = fields.Char(default=lambda self: _("New"), copy=False, readonly=True)
    service_order_id = fields.Many2one("service.order", tracking=True)
    helpdesk_ticket_id = fields.Many2one("helpdesk.ticket", tracking=True)
    customer_id = fields.Many2one("res.partner", required=True, tracking=True)
    customer_ref = fields.Char()
    assigned_to = fields.Many2one("res.users", tracking=True)
    repair_type = fields.Selection(
        [("onsite", "Onsite"), ("offsite", "Offsite")],
        default="onsite",
        required=True,
        tracking=True,
    )
    product_id = fields.Many2one("product.product", tracking=True)
    lot_id = fields.Many2one(
        "stock.lot",
        string="Serial / Lot",
        domain="[('product_id', '=', product_id)]",
        tracking=True,
    )
    issue_description = fields.Html(required=True)
    inspection_result = fields.Html()
    solution_description = fields.Html()
    new_product_discussion = fields.Html()
    amc_discussion = fields.Html()
    estimated_amount = fields.Monetary(tracking=True)
    advance_amount = fields.Monetary(tracking=True)
    currency_id = fields.Many2one(
        "res.currency",
        default=lambda self: self.env.company.currency_id,
        required=True,
    )
    advance_status = fields.Selection(
        [("not_required", "Not Required"), ("pending", "Pending"), ("received", "Received")],
        default="not_required",
        tracking=True,
    )
    customer_approval_status = fields.Selection(
        [("not_required", "Not Required"), ("pending", "Pending"), ("approved", "Approved"), ("rejected", "Rejected")],
        default="pending",
        tracking=True,
    )
    issue_photo_ids = fields.Many2many(
        "ir.attachment",
        "x_savi_service_repair_issue_photo_rel",
        "repair_id",
        "attachment_id",
        string="Issue Photos",
        copy=False,
    )
    solution_photo_ids = fields.Many2many(
        "ir.attachment",
        "x_savi_service_repair_solution_photo_rel",
        "repair_id",
        "attachment_id",
        string="Solution Photos",
        copy=False,
    )
    document_ids = fields.Many2many(
        "ir.attachment",
        "x_savi_service_repair_document_rel",
        "repair_id",
        "attachment_id",
        string="Documents",
        copy=False,
    )
    state = fields.Selection(
        [
            ("draft", "Draft"),
            ("inspection", "Inspection"),
            ("estimate", "Estimate"),
            ("approved", "Approved"),
            ("repair", "Repair"),
            ("done", "Done"),
            ("cancel", "Cancelled"),
        ],
        default="draft",
        required=True,
        tracking=True,
    )
    company_id = fields.Many2one(
        "res.company",
        default=lambda self: self.env.company,
        required=True,
    )

    @api.onchange("service_order_id")
    def _onchange_service_order_id(self):
        for repair in self:
            order = repair.service_order_id
            if order:
                repair.customer_id = order.customer_id
                repair.customer_ref = order.customer_ref
                repair.assigned_to = order.assigned_to
                repair.company_id = order.company_id

    @api.model_create_multi
    def create(self, vals_list):
        for vals in vals_list:
            if vals.get("name", _("New")) == _("New"):
                vals["name"] = self.env["ir.sequence"].next_by_code("x_savi.service.repair") or _("New")
        return super().create(vals_list)

    def action_start_inspection(self):
        self.write({"state": "inspection"})

    def action_send_estimate(self):
        self.write({"state": "estimate"})

    def action_customer_approve(self):
        self.write({"state": "approved", "customer_approval_status": "approved"})

    def action_start_repair(self):
        self.write({"state": "repair"})

    def action_done(self):
        self.write({"state": "done"})

    def action_cancel(self):
        self.write({"state": "cancel"})

    def action_reset_draft(self):
        self.write({"state": "draft"})
