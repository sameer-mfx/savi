from odoo import api, fields, models, _


class ProjectClosure(models.Model):
    _name = "x_savi.project.closure"
    _description = "SAVI Project Closure and Audit"
    _inherit = ["mail.thread", "mail.activity.mixin"]
    _order = "completion_date desc, id desc"

    name = fields.Char(default=lambda self: _("New"), copy=False, readonly=True)
    project_id = fields.Many2one("project.project", required=True, tracking=True)
    partner_id = fields.Many2one(related="project_id.partner_id", store=True, readonly=True)
    completion_date = fields.Date(default=fields.Date.context_today, required=True, tracking=True)
    final_testing_done = fields.Boolean(tracking=True)
    handover_done = fields.Boolean(tracking=True)
    completion_certificate_received = fields.Boolean(tracking=True)
    testimonial_received = fields.Boolean(tracking=True)
    website_photos_collected = fields.Boolean(tracking=True)
    customer_feedback = fields.Html()
    audit_notes = fields.Html()
    revenue_amount = fields.Monetary()
    expense_amount = fields.Monetary()
    profit_amount = fields.Monetary(compute="_compute_profit_amount", store=True)
    currency_id = fields.Many2one(
        "res.currency",
        default=lambda self: self.env.company.currency_id,
        required=True,
    )
    handover_document_ids = fields.Many2many(
        "ir.attachment",
        "x_savi_project_closure_handover_rel",
        "closure_id",
        "attachment_id",
        string="Handover Documents",
        copy=False,
    )
    completion_photo_ids = fields.Many2many(
        "ir.attachment",
        "x_savi_project_closure_photo_rel",
        "closure_id",
        "attachment_id",
        string="Completion Photos",
        copy=False,
    )
    state = fields.Selection(
        [("draft", "Draft"), ("submitted", "Submitted"), ("approved", "Approved"), ("cancel", "Cancelled")],
        default="draft",
        required=True,
        tracking=True,
    )
    company_id = fields.Many2one(
        "res.company",
        default=lambda self: self.env.company,
        required=True,
    )

    @api.depends("revenue_amount", "expense_amount")
    def _compute_profit_amount(self):
        for closure in self:
            closure.profit_amount = closure.revenue_amount - closure.expense_amount

    def action_submit(self):
        for closure in self:
            if closure.name == _("New"):
                closure.name = self.env["ir.sequence"].next_by_code("x_savi.project.closure") or _("New")
            closure.state = "submitted"

    def action_approve(self):
        self.write({"state": "approved"})

    def action_reset_draft(self):
        self.write({"state": "draft"})

    def action_cancel(self):
        self.write({"state": "cancel"})
