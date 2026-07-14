from odoo import fields, models, _


class ProjectDailyReport(models.Model):
    _name = "x_savi.project.daily.report"
    _description = "SAVI Project Daily Site Report"
    _inherit = ["mail.thread", "mail.activity.mixin"]
    _order = "report_date desc, id desc"

    name = fields.Char(default=lambda self: _("New"), copy=False, readonly=True)
    project_id = fields.Many2one("project.project", required=True, tracking=True)
    task_id = fields.Many2one(
        "project.task",
        domain="[('project_id', '=', project_id)]",
        tracking=True,
    )
    partner_id = fields.Many2one(related="project_id.partner_id", store=True, readonly=True)
    report_date = fields.Date(default=fields.Date.context_today, required=True, tracking=True)
    period = fields.Selection(
        [("morning", "Morning"), ("evening", "Evening"), ("full_day", "Full Day")],
        default="full_day",
        required=True,
        tracking=True,
    )
    responsible_id = fields.Many2one(
        "res.users",
        default=lambda self: self.env.user,
        required=True,
        tracking=True,
    )
    engineer_ids = fields.Many2many("hr.employee", string="Engineers / Team")
    work_done = fields.Html(required=True)
    blockers = fields.Html()
    material_used = fields.Html()
    next_plan = fields.Html()
    site_image_ids = fields.Many2many(
        "ir.attachment",
        "x_savi_project_daily_report_image_rel",
        "report_id",
        "attachment_id",
        string="Site Photos",
        copy=False,
    )
    document_ids = fields.Many2many(
        "ir.attachment",
        "x_savi_project_daily_report_doc_rel",
        "report_id",
        "attachment_id",
        string="Documents",
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

    def action_submit(self):
        for report in self:
            if report.name == _("New"):
                report.name = self.env["ir.sequence"].next_by_code("x_savi.project.daily.report") or _("New")
            report.state = "submitted"

    def action_approve(self):
        self.write({"state": "approved"})

    def action_reset_draft(self):
        self.write({"state": "draft"})

    def action_cancel(self):
        self.write({"state": "cancel"})
