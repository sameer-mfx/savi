# -*- coding: utf-8 -*-
from odoo import models, fields, api, _
from odoo.exceptions import ValidationError
from datetime import datetime, time, timedelta
import pytz

class HrAttendance(models.Model):
    _inherit = 'hr.attendance'

    @api.model
    def automate_employee_attendance(self):
        """Automatically set check_out for open attendances
        using the employee or user timezone and company work_end_time.
        """
        self = self.sudo()
        open_attendances = self.search([('check_in', '!=', False), ('check_out', '=', False)])
        if not open_attendances:
            return

        for att in open_attendances:
            tz = self._get_timezone(att)
            check_in_local = self._to_local(att.check_in, tz)

            # Convert float work_end_time -> HH:MM
            end_float = att.employee_id.company_id.work_end_time or 0.0
            hours, minutes = self._float_to_hm(end_float)

            # Build local checkout on same local date as check_in
            local_checkout = tz.localize(datetime.combine(check_in_local.date(), time(hour=hours, minute=minutes)))
            checkout_utc = self._to_utc(local_checkout)

            # Safety: ensure checkout >= check_in
            if checkout_utc < att.check_in:
                local_checkout += timedelta(days=1)
                checkout_utc = self._to_utc(local_checkout)

            att.write({'check_out': checkout_utc})

    # ------------------------------
    # Helpers
    # ------------------------------
    def _get_timezone(self, att):
        """Return pytz timezone for employee → user → UTC."""
        tz_name = att.employee_id.user_id.tz or self.env.user.tz or 'UTC'
        try:
            return pytz.timezone(tz_name)
        except Exception:
            return pytz.UTC

    def _to_local(self, dt_utc, tz):
        """Convert naive UTC datetime to local timezone datetime."""
        return dt_utc.replace(tzinfo=pytz.UTC).astimezone(tz)

    def _to_utc(self, dt_local):
        """Convert localized datetime back to naive UTC datetime."""
        return dt_local.astimezone(pytz.UTC).replace(tzinfo=None)

    def _float_to_hm(self, value):
        """Convert float (e.g., 8.5) → (8, 30)."""
        hours = int(value)
        minutes = int(round((value - hours) * 60))
        return hours, minutes


class ResCompany(models.Model):
    _inherit = 'res.company'

    work_start_time = fields.Float(
        string='Work Start Time',
        help="Company default work start time (HH:MM).",
    )
    work_end_time = fields.Float(
        string='Work End Time',
        help="Company default work end time (HH:MM).",
    )

    @api.constrains('work_start_time', 'work_end_time')
    def _check_work_times(self):
        for company in self:
            start, end = company.work_start_time, company.work_end_time
            if not (0.0 <= start < 24.0):
                raise ValidationError(_("Work start time must be between 00:00 and 23:59."))
            if not (0.0 <= end < 24.0):
                raise ValidationError(_("Work end time must be between 00:00 and 23:59."))
            if end <= start:
                raise ValidationError(_("Work end time must be later than work start time."))