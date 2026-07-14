from odoo import fields, models, _

from .message_utils import savi_param_bool


class ServiceOrder(models.Model):
    _inherit = "service.order"

    savi_assignment_activity_created = fields.Boolean(
        string="SAVI Assignment Activity Created",
        copy=False,
        readonly=True,
    )
    savi_assignment_email_sent = fields.Boolean(
        string="SAVI Assignment Email Sent",
        copy=False,
        readonly=True,
    )
    savi_assignment_email_sent_date = fields.Datetime(
        string="SAVI Assignment Email Sent On",
        copy=False,
        readonly=True,
    )

    def write(self, vals):
        result = super().write(vals)
        if "assigned_to" in vals or vals.get("state") == "approved":
            self._savi_process_service_assignment()
        return result

    def _savi_process_service_assignment(self):
        for order in self:
            if not order.assigned_to:
                continue
            order._savi_schedule_assignment_activity()
            order._savi_send_assignment_email()

    def _savi_schedule_assignment_activity(self):
        self.ensure_one()
        if (
            not savi_param_bool(self.env, "service_assignment_activity_enabled", default=True)
            or self.savi_assignment_activity_created
        ):
            return
        deadline = fields.Date.context_today(self)
        if self.visit_date:
            deadline = fields.Date.to_date(self.visit_date)
        self.activity_schedule(
            "mail.mail_activity_data_todo",
            date_deadline=deadline,
            summary=_("Service Visit Assigned: %s") % self.name,
            note=_("Please attend the assigned service visit for %s.") % (
                self.customer_id.display_name or _("the customer")
            ),
            user_id=self.assigned_to.id,
        )
        self.savi_assignment_activity_created = True

    def _savi_send_assignment_email(self):
        self.ensure_one()
        if (
            not savi_param_bool(self.env, "service_assignment_customer_email_enabled")
            or self.savi_assignment_email_sent
            or not self.customer_id.email
        ):
            return
        template = self.env.ref(
            "savi_message_automation.email_template_service_assignment",
            raise_if_not_found=False,
        )
        if not template:
            return
        template.send_mail(self.id, force_send=True)
        self.write({
            "savi_assignment_email_sent": True,
            "savi_assignment_email_sent_date": fields.Datetime.now(),
        })
