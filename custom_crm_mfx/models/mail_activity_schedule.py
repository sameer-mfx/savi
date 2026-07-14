from odoo import models, _
from odoo.tools.misc import clean_context

class MailActivity(models.Model):
    _inherit = 'mail.activity'

    def action_feedback_schedule_next(self, feedback=False, attachment_ids=None):
        ctx = dict(
            clean_context(self.env.context),
            default_previous_activity_type_id=self.activity_type_id.id,
            activity_previous_deadline=self.date_deadline,
            default_res_id=self.res_id,
            default_res_model=self.res_model,
            default_summary=self.summary,
            default_user_id=self.user_id.id,
            default_reference=f"{self.res_model},{self.res_id}",
        )
        _messages, next_activities = self._action_done(feedback=feedback, attachment_ids=attachment_ids)  # will unlink activity, dont access self after that
        if next_activities:
            return False
        return {
            'name': _('Schedule an Activity'),
            'context': ctx,
            'view_mode': 'form',
            'res_model': 'mail.activity',
            'views': [(False, 'form')],
            'type': 'ir.actions.act_window',
            'target': 'new',
        }