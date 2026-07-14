from dateutil.relativedelta import relativedelta

from odoo import fields, models, _

from .message_utils import savi_param_bool, savi_param_int


class AmcOrder(models.Model):
    _inherit = "amc.order"

    savi_renewal_reminder_sent = fields.Boolean(
        string="SAVI Renewal Reminder Sent",
        copy=False,
        readonly=True,
    )
    savi_renewal_reminder_sent_date = fields.Datetime(
        string="SAVI Renewal Reminder Sent On",
        copy=False,
        readonly=True,
    )

    def _cron_savi_amc_renewal_reminders(self):
        days = max(savi_param_int(self.env, "amc_renewal_days", 30), 1)
        today = fields.Date.today()
        reminder_until = today + relativedelta(days=days)
        orders = self.search([
            ("state", "=", "approved"),
            ("amc_end_date", "!=", False),
            ("amc_end_date", ">=", today),
            ("amc_end_date", "<=", reminder_until),
            ("savi_renewal_reminder_sent", "=", False),
        ])
        for order in orders:
            order._savi_process_amc_renewal_reminder()

    def _savi_process_amc_renewal_reminder(self):
        self.ensure_one()
        activity_created = self._savi_schedule_renewal_activity()
        email_sent = self._savi_send_renewal_email()
        if activity_created or email_sent:
            self.write({
                "savi_renewal_reminder_sent": True,
                "savi_renewal_reminder_sent_date": fields.Datetime.now(),
            })

    def _savi_schedule_renewal_activity(self):
        self.ensure_one()
        if not savi_param_bool(self.env, "amc_renewal_activity_enabled", default=True):
            return False
        existing = self.env["mail.activity"].search([
            ("res_model", "=", "amc.order"),
            ("res_id", "=", self.id),
            ("summary", "=", _("AMC Renewal Follow-up")),
        ], limit=1)
        if existing:
            return False
        self.activity_schedule(
            "mail.mail_activity_data_todo",
            date_deadline=self.amc_end_date,
            summary=_("AMC Renewal Follow-up"),
            note=_("AMC %s for %s is due for renewal on %s.") % (
                self.name,
                self.partner_id.display_name or _("Customer"),
                self.amc_end_date,
            ),
            user_id=self.user_id.id or self.env.user.id,
        )
        return True

    def _savi_send_renewal_email(self):
        self.ensure_one()
        if (
            not savi_param_bool(self.env, "amc_renewal_customer_email_enabled")
            or not self.partner_id.email
        ):
            return False
        template = self.env.ref(
            "savi_message_automation.email_template_amc_renewal_reminder",
            raise_if_not_found=False,
        )
        if not template:
            return False
        template.send_mail(self.id, force_send=True)
        return True
