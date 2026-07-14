# -*- coding: utf-8 -*-
# Part of Softhealer Technologies.

from odoo import models, fields, api, modules, exceptions, _,Command
from datetime import datetime, timedelta
from dateutil.relativedelta import relativedelta
from odoo.tools.misc import clean_context
from odoo.tools import DEFAULT_SERVER_DATE_FORMAT
from odoo.tools import html2plaintext
import math
from odoo.osv import expression
from collections import defaultdict
from odoo.http import request
import json
import logging
import uuid
from odoo.tools import SQL
import pytz

from odoo.exceptions import ValidationError, UserError
_logger = logging.getLogger('odoo.addons.base.partner.merge')


class MailActivityMixin(models.AbstractModel):
    _inherit = 'mail.activity.mixin'

    def _read_group_groupby(self, groupby_spec, query):
        if groupby_spec != 'activity_state':
            return super()._read_group_groupby(groupby_spec, query)

        self.env['mail.activity'].flush_model(['res_model', 'res_id', 'user_id', 'date_deadline'])

        tz = 'UTC'
        if self.env.context.get('tz') in pytz.all_timezones_set:
            tz = self.env.context['tz']

        sql_join = SQL(
            """
            (SELECT res_id,
                CASE
                    WHEN min(date_deadline - (now() AT TIME ZONE COALESCE(res_partner.tz, %(tz)s))::date) > 0 THEN 'planned'
                    WHEN min(date_deadline - (now() AT TIME ZONE COALESCE(res_partner.tz, %(tz)s))::date) < 0 THEN 'overdue'
                    WHEN min(date_deadline - (now() AT TIME ZONE COALESCE(res_partner.tz, %(tz)s))::date) = 0 THEN 'today'
                    ELSE null
                END AS activity_state
            FROM mail_activity
            JOIN res_users ON (res_users.id = mail_activity.user_id)
            JOIN res_partner ON (res_partner.id = res_users.partner_id)
            WHERE res_model = %(res_model)s and mail_activity.active = True
            GROUP BY res_id)
            """,
            res_model=self._name,
            tz=tz,
        )
        alias = query.join(self._table, "id", sql_join, "res_id", "last_activity_state")

        return SQL.identifier(alias, 'activity_state'), ['activity_state']



class MailActivity(models.Model):
    """ Inherited Mail Acitvity to add custom field"""
    _name = 'mail.activity'
    _inherit = ['portal.mixin','mail.activity']


    # portal.mixin override
    def _compute_access_url(self):
        super()._compute_access_url()
        for order in self:
            order.access_url = f'/my/activities/{order.id}'

    def _default_access_token(self):
        return uuid.uuid4().hex

    @api.model
    def default_company_id(self):
        return self.env.company

    active = fields.Boolean(default=True)
    supervisor_id = fields.Many2one('res.users',default=lambda self: self.env.user, string="Supervisor",domain=[('share','=',False)])
    sh_activity_tags = fields.Many2many(
        "sh.activity.tags", string='Activity Tags')
    state = fields.Selection(
        selection_add=[("done", "Done"),("cancel","Cancelled")],
        search = '_search_state'
    )
    sh_state = fields.Selection([('overdue','Overdue'),('today','Today'),('planned','Planned'),('done','Done'),('cancel','Cancelled')])
    date_done = fields.Date("Completed Date", index=True, readonly=True)
    feedback = fields.Text("Feedback")

    text_note = fields.Char("Notes In Char format ",
                            compute='_compute_html_to_char_note')
    sh_user_ids = fields.Many2many('res.users', string="Assign Multi Users",domain=[('share','=',False)])
    sh_display_multi_user = fields.Boolean(
        compute='_compute_sh_display_multi_user')
    company_id = fields.Many2one(
        'res.company', string='Company', default=default_company_id)
    color = fields.Integer('Color Index', default=0)
    sh_create_individual_activity = fields.Boolean(
        'Individual activities for multi users ?')
    sh_activity_alarm_ids = fields.Many2many('sh.activity.alarm',string = 'Reminders')
    sh_date_deadline = fields.Datetime('Reminder Due Date', default=lambda self: fields.Datetime.now())
    activity_cancel = fields.Boolean()
    activity_done = fields.Boolean()
    sh_activity_id = fields.Many2one("sh.recurring.activities", ondelete="cascade")
    reference = fields.Reference(string='Related Document',
        selection='_reference_models')


    def unlink(self):
        # Unlink Activity - From Activity Menu
        if self.env.context.get('is_from_activity_menu'):
            return super(MailActivity, self).unlink()

        for rec in self:
            rec._compute_state()
            model_name = rec.res_model.replace(".", "_")
            self.env.cr.execute("Select id from "+(model_name) + " where id = "+(str(rec.res_id)))
            origin_record_id = self._cr.fetchall()
            if not origin_record_id:
                return super(MailActivity, self).unlink()
            else:
                # For Cancel activity from chatter
                rec.state = 'cancel'
                rec.active = False
                rec.date_done = False
                rec.activity_cancel = True
                rec._compute_state()
        return False


    @api.model
    def _reference_models(self):
        all_dic = {}
        models_list = []
        models = request.env['ir.model'].sudo().search([('state', '!=', 'manual')])
        if models:
            for model_id in models:
                if model_id.state != 'manual':
                    field_id = request.env['ir.model.fields'].sudo().search([('name','=','activity_ids'),('model_id','=',model_id.id),('store','=',True)])
                    if field_id:
                        models_list.append(model_id.id)
        models = request.env['ir.model'].sudo().search([('id', 'in',models_list)])
        return [(model.model, model.name)
                for model in models
                if not model.model.startswith('ir.')]

    def update_activities(self):
        IrModel = self.env['ir.model']
        IrField = self.env['ir.model.fields']
        for activity in self:
            record=self.env[activity.res_model].browse(activity.res_id)
            if not record.exists():
                continue

            model = IrModel.sudo().search([('model', '=', activity.res_model)], limit=1)
            if not model:
                continue

            company_field = IrField.sudo().search([
                ('model_id', '=', model.id),
                ('ttype', '=', 'many2one'),
                ('relation', '=', 'res.company'),
            ],limit=1)

            if not company_field:
                continue

            company_value = False
            if company_field.name in record:
                company_value = record[company_field.name]

            if company_value and activity.company_id.id != company_value.id:
                activity.company_id = company_value.id

    @api.onchange('reference')
    def onchange_reference(self):
        if self.reference:
            if self.reference._name:
                model_id = self.env['ir.model'].sudo().search([('model','=',self.reference._name)],limit=1)
                if model_id:
                    self.res_model_id = model_id.id
                    self.res_id = self.reference.id
                    self.res_model = self.reference._name

    @api.depends('res_model', 'res_id')
    def _compute_res_name(self):
        for activity in self:
            activity.res_name = ''
            if activity.res_model and activity.res_id:
                activity.reference = f"{activity.res_model},{activity.res_id}"
                activity.res_name = self.env[activity.res_model].browse(activity.res_id).display_name
                # activity.res_name = self.env[activity.res_model].browse(activity.res_id).name_get()[0][1]

    @api.onchange('state')
    def onchange_state(self):
        self.ensure_one()
        self.activity_done = False
        self.activity_cancel = False
        self._compute_state()

    @api.depends('date_deadline')
    def _compute_state(self):
        super(MailActivity, self)._compute_state()
        for record in self.filtered(lambda activity: not activity.active):
            if record.activity_cancel:
                record.state = 'cancel'
            if record.activity_done:
                record.state = 'done'
        for activity_record in self.filtered(lambda activity: activity.active):
            activity_record.sh_state = activity_record.state

    def write(self, vals):

        if self:
            for rec in self:
                if vals.get('sh_create_individual_activity') and vals.get('sh_user_ids'):
                    # For individual activity
                    # Extract user IDs from the command list
                    user_ids = []
                    for cmd in vals['sh_user_ids']:
                        if cmd[0] == 6:  # REPLACE command
                            user_ids = cmd[2]
                        elif cmd[0] in (1, 2, 3, 4):  # Other commands that affect the relationship
                            if cmd[0] == 4:  # ADD ONE
                                user_ids.append(cmd[1])
                            elif cmd[0] == 3:  # REMOVE ONE
                                if cmd[1] in user_ids:
                                    user_ids.remove(cmd[1])
                    # Store extracted user IDs for later processing
                    for uid in user_ids:
                        if uid != rec.user_id.id:
                            self.env['mail.activity'].sudo().create({
                            'user_id': uid,
                            'res_model_id': rec.res_model_id.id,
                            'res_id': rec.res_id,
                            'date_deadline': vals.get('date_deadline', rec.date_deadline),
                            'sh_user_ids': [(6, 0, [uid])],
                            'supervisor_id': rec.supervisor_id.id,
                            'activity_type_id': rec.activity_type_id.id,
                            'summary': vals.get('summary', rec.summary),
                            'sh_activity_tags': [(6, 0, rec.sh_activity_tags.ids)],
                            'note': vals.get('note', rec.note),
                            'sh_create_individual_activity': False,  # Prevent recursion
                        })
                    # For individual activity
                if vals.get('state'):
                    vals.update({
                        'sh_state':vals.get('state')
                        })
                if vals.get('active') and vals.get('active') == True:
                    rec.onchange_state()
        return super(MailActivity, self).write(vals)


    def _search_state(self,operator,value):
        not_done_ids = []
        done_ids = []
        if value == 'done':
            for record in self.search([('active','=',False),('date_done','!=',False)]):
                done_ids.append(record.id)
        elif value == 'cancel':
            for record in self.search([('active','=',False),('date_done','=',False)]):
                done_ids.append(record.id)
        elif value == 'today':
            for record in self.search([('date_deadline','=',fields.Date.today())]):
                done_ids.append(record.id)
        elif value == 'planned':
            for record in self.search([('date_deadline','>',fields.Date.today())]):
                done_ids.append(record.id)
        elif value == 'overdue':
            for record in self.search([('date_deadline','<',fields.Date.today())]):
                done_ids.append(record.id)
        if operator == '=':
            return [('id', 'in', done_ids)]
        elif operator == 'in':
            return [('id', 'in', done_ids)]
        elif operator == '!=':
            return [('id', 'in', not_done_ids)]
        elif operator == 'not in':
            return [('id', 'in', not_done_ids)]
        else:
            return []

    @api.onchange('date_deadline')
    def _onchange_sh_date_deadline(self):
        if self:
            for rec in self:
                if rec.date_deadline:
                    rec.sh_date_deadline = rec.date_deadline + timedelta(hours=0, minutes=0, seconds=0)

    @api.model_create_multi
    def create(self, vals_list):
        for vals in vals_list:
            # If Not Added model
            if not vals.get('res_model_id'):
                if not vals.get('reference'):
                    raise UserError('Please add a related document before creating an activity')
            # If Not Added model
            if vals.get('res_model_id'):
                model_id = self.env['ir.model'].sudo().search([('id','=',vals.get('res_model_id'))],limit=1)
                if model_id:
                    if 'activity_ids' not in self.env[model_id.model]._fields:
                        raise UserError('You can not create activity for this model due to this model does not have activity field.')
        result = super(MailActivity, self).create(vals_list)
        for res in result:
            if res.sh_user_ids and res.sh_create_individual_activity:
                for user in res.sh_user_ids:
                    if res.user_id.id != user.id:
                        created_activity=self.env['mail.activity'].sudo().create({
                            'user_id':user.id,
                            'res_model_id': res.res_model_id.id,
                            'res_id': res.res_id,
                            'date_deadline': res.date_deadline,
                            'sh_user_ids': [(6, 0, user.ids)],
                            'supervisor_id': res.supervisor_id.id,
                            'activity_type_id': res.activity_type_id.id,
                            'summary': res.summary,
                            'sh_activity_tags': [(6, 0, res.sh_activity_tags.ids)],
                            'note': res.note,
                        })
            if res.state:
                res.sh_state = res.state
        return result

    @api.model
    def action_cancel_dashboard(self,activity_id):
        mail_activity_id = self.env['mail.activity'].sudo().browse(int(activity_id))
        if mail_activity_id:
            mail_activity_id.action_cancel()
            if mail_activity_id.state == 'cancel':
                return {'cancelled':True}

    def action_cancel(self):
        if self:
            for rec in self:
                rec.state = 'cancel'
                rec.active = False
                rec.date_done = False
                rec.activity_cancel = True
                rec._compute_state()

    @api.model
    def unarchive_dashboard(self,activity_id):
        mail_activity_id = self.env['mail.activity'].sudo().browse(int(activity_id))
        if mail_activity_id:
            mail_activity_id.unarchive()
            return {'unarchive':True}

    @api.model
    def action_done_dashboard(self,activity_id,activity_feedback):
        mail_activity_id = self.env['mail.activity'].sudo().browse(int(activity_id))
        if mail_activity_id:
            mail_activity_id.action_feedback(feedback = activity_feedback,attachment_ids=None)
            if mail_activity_id.state == 'done':
                return {'completed':True}

    def unarchive(self,active=True):
        self.ensure_one()
        self.activity_cancel = False
        self.active = True
        self._compute_state()

    @api.depends('company_id')
    def _compute_sh_display_multi_user(self):
        if self:
            for rec in self:
                rec.sh_display_multi_user = False
                if rec.company_id and rec.company_id.sh_display_multi_user:
                    rec.sh_display_multi_user = True

    def _compute_html_to_char_note(self):
        if self:
            for rec in self:
                if rec.note:
                    rec.text_note = html2plaintext(rec.note)
                else:
                    rec.text_note = ''

    @api.model
    def notify_mail_activity_fun(self):

        template = self.env.ref(
            'sh_activities_management.template_mail_activity_due_notify_email')
        notify_create_user_template = self.env.ref(
            'sh_activities_management.template_mail_activity_due_notify_email_create_user')
        company_object = self.env['res.company'].search(
            [('activity_due_notification', '=', True)], limit=1)

        if template and company_object and company_object.activity_due_notification:

            activity_obj = self.env['mail.activity'].search([])

            if activity_obj:
                for record in activity_obj:
                    if record.date_deadline and record.user_id and record.user_id.id != self.env.ref('base.user_root').id and record.user_id.partner_id and record.user_id.partner_id.email:

                        # On Due Date
                        if company_object.ondue_date_notify:

                            if datetime.strptime(str(record.date_deadline), DEFAULT_SERVER_DATE_FORMAT).date() == datetime.now().date():
                                template.send_mail(record.id, force_send=True)
                                if notify_create_user_template and company_object.notify_create_user_due:
                                    if record.user_id.id != record.create_uid.id and record.create_uid.id != self.env.ref('base.user_root').id:
                                        notify_create_user_template.send_mail(
                                            record.id, force_send=True)
                        # On After First Notify
                        if company_object.after_first_notify and company_object.enter_after_first_notify:
                            after_date = datetime.strptime(str(record.date_deadline), DEFAULT_SERVER_DATE_FORMAT).date(
                            ) + timedelta(days=company_object.enter_after_first_notify)

                            if after_date == datetime.now().date():
                                template.send_mail(record.id, force_send=True)
                                if notify_create_user_template and company_object.notify_create_user_after_first:
                                    if record.user_id.id != record.create_uid.id and record.create_uid.id != self.env.ref('base.user_root').id:
                                        notify_create_user_template.send_mail(
                                            record.id, force_send=True)
                        # On After Second Notify
                        if company_object.after_second_notify and company_object.enter_after_second_notify:
                            after_date = datetime.strptime(str(record.date_deadline), DEFAULT_SERVER_DATE_FORMAT).date(
                            ) + timedelta(days=company_object.enter_after_second_notify)

                            if after_date == datetime.now().date():
                                template.send_mail(record.id, force_send=True)
                                if notify_create_user_template and company_object.notify_create_user_after_second:
                                    if record.user_id.id != record.create_uid.id and record.create_uid.id != self.env.ref('base.user_root').id:
                                        notify_create_user_template.send_mail(
                                            record.id, force_send=True)
                        # On Before First Notify
                        if company_object.before_first_notify and company_object.enter_before_first_notify:
                            before_date = datetime.strptime(str(record.date_deadline), DEFAULT_SERVER_DATE_FORMAT).date(
                            ) - timedelta(days=company_object.enter_before_first_notify)

                            if before_date == datetime.now().date():
                                template.send_mail(record.id, force_send=True)
                                if notify_create_user_template and company_object.notify_create_user_before_first:
                                    if record.user_id.id != record.create_uid.id and record.create_uid.id != self.env.ref('base.user_root').id:
                                        notify_create_user_template.send_mail(
                                            record.id, force_send=True)
                        # On Before Second Notify
                        if company_object.before_second_notify and company_object.enter_before_second_notify:
                            before_date = datetime.strptime(str(record.date_deadline), DEFAULT_SERVER_DATE_FORMAT).date(
                            ) - timedelta(days=company_object.enter_before_second_notify)

                            if before_date == datetime.now().date():
                                template.send_mail(record.id, force_send=True)
                                if notify_create_user_template and company_object.notify_create_user_before_second:
                                    if record.user_id.id != record.create_uid.id and record.create_uid.id != self.env.ref('base.user_root').id:
                                        notify_create_user_template.send_mail(
                                            record.id, force_send=True)

    def action_view_activity(self):
        self.ensure_one()
        try:
            self.env[self.res_model].browse(
                self.res_id).check_access_rule('read')
            return{
                'name': 'Origin Activity',
                'res_model': self.res_model,
                'res_id': self.res_id,
                'view_mode': 'form',
                'type': 'ir.actions.act_window',
                'target': 'current',
            }
        except exceptions.AccessError:
            raise exceptions.UserError(
                _('Assigned user %s has no access to the document and is not able to handle this activity.') %
                self.env.user.display_name)

    def action_edit_activity(self):
        self.ensure_one()
        view_id = self.env.ref(
            'sh_activities_management.sh_mail_activity_type_view_form_inherit').id
        return {
            'name': _('Schedule an Activity'),
            'view_mode': 'form',
            'res_model': 'mail.activity',
            'views': [(view_id, 'form')],
            'res_id':self.id,
            'type': 'ir.actions.act_window',
            'target': 'new',
        }

    def action_done(self):
        """ Wrapper without feedback because web button add context as
        parameter, therefore setting context to feedback """
        return{
            'name': 'Activity Feedback',
            'res_model': 'activity.feedback',
            'type': 'ir.actions.act_window',
            'view_mode': 'form',
            'context': {'default_done_button_pressed': True},
            'target': 'new',
        }

    def action_feedback(self, feedback=False, attachment_ids=None):
        self.state = 'done'
        self.active = False
        self.activity_done = True
        self._compute_state()
        if self.state == 'done':
            self.date_done = fields.Date.today()
        self.feedback = feedback
        messages, _next_activities = self.with_context(
            clean_context(self.env.context)
        )._action_done(feedback=feedback, attachment_ids=attachment_ids)
        return messages[0].id if messages else False
        # return messages[0].id if messages else False

    def action_done_from_popup(self, feedback=False):
        self.ensure_one()
        self = self.with_context(clean_context(self.env.context))
        messages, next_activities = self._action_done(
            feedback=feedback, attachment_ids=False)
        self.state = 'done'
        self.active = False
        self.activity_done = True
        self._compute_state()
        if self.state == 'done':
            self.date_done = fields.Date.today()
        self.feedback = feedback
#         return messages.ids and messages.ids[0] or False

    def _action_done(self, feedback=False, attachment_ids=None):
        """ Private implementation of marking activity as done: posting a message, deleting activity
            (since done), and eventually create the automatical next activity (depending on config).
            :param feedback: optional feedback from user when marking activity as done
            :param attachment_ids: list of ir.attachment ids to attach to the posted mail.message
            :returns (messages, activities) where
                - messages is a recordset of posted mail.message
                - activities is a recordset of mail.activity of forced automically created activities
        """
        # marking as 'done'
        messages = self.env['mail.message']
        next_activities_values = []

        # Search for all attachments linked to the activities we are about to unlink. This way, we
        # can link them to the message posted and prevent their deletion.
        attachments = self.env['ir.attachment'].search_read([
            ('res_model', '=', self._name),
            ('res_id', 'in', self.ids),
        ], ['id', 'res_id'])

        activity_attachments = defaultdict(list)
        for attachment in attachments:
            activity_id = attachment['res_id']
            activity_attachments[activity_id].append(attachment['id'])

        for model, activity_data in self._classify_by_model().items():
            # Allow user without access to the record to "mark as done" activities assigned to them. At the end of the
            # method, the activity is unlinked or archived which ensure the user has enough right on the activities.
            records_sudo = self.env[model].sudo().browse(activity_data['record_ids'])
            for record_sudo, activity in zip(records_sudo, activity_data['activities']):
                # extract value to generate next activities
                if activity.chaining_type == 'trigger':
                    vals = activity.with_context(activity_previous_deadline=activity.date_deadline)._prepare_next_activity_values()
                    next_activities_values.append(vals)

                # post message on activity, before deleting it
                activity_message = record_sudo.message_post_with_source(
                    'mail.message_activity_done',
                    attachment_ids=attachment_ids,
                    author_id=self.env.user.partner_id.id,
                    render_values={
                        'activity': activity,
                        'feedback': feedback,
                        'display_assignee': activity.user_id != self.env.user
                    },
                    mail_activity_type_id=activity.activity_type_id.id,
                    subtype_xmlid='mail.mt_activities',
                )
                if activity.activity_type_id.keep_done:
                    attachment_ids = (attachment_ids or []) + activity_attachments.get(activity.id, [])
                    if attachment_ids:
                        activity.attachment_ids = attachment_ids

                # Moving the attachments in the message
                # TODO: Fix void res_id on attachment when you create an activity with an image
                # directly, see route /web_editor/attachment/add
                if activity_attachments[activity.id]:
                    message_attachments = self.env['ir.attachment'].browse(activity_attachments[activity.id])
                    if message_attachments:
                        message_attachments.write({
                            'res_id': activity_message.id,
                            'res_model': activity_message._name,
                        })
                        activity_message.attachment_ids = message_attachments
                messages += activity_message

        next_activities = self.env['mail.activity']
        if next_activities_values:
            next_activities = self.env['mail.activity'].create(next_activities_values)

        # activity_to_keep = self.filtered('activity_type_id.keep_done')
        # activity_to_keep.action_archive()
        # (self - activity_to_keep).unlink()  # will unlink activity, dont access `self` after that

        self.active = False
        self.date_done = fields.Date.today()
        self.feedback = feedback
        self.state = "done"
        self.activity_done = True
        self._compute_state()

        return messages, next_activities

    def activity_format(self):
        self = self.filtered(lambda r: r.active == True)
        activities = self.read()
        mail_template_ids = set([template_id for activity in activities for template_id in activity["mail_template_ids"]])
        mail_template_info = self.env["mail.template"].browse(mail_template_ids).read(['id', 'name'])
        mail_template_dict = dict([(mail_template['id'], mail_template) for mail_template in mail_template_info])
        for activity in activities:
            activity['mail_template_ids'] = [mail_template_dict[mail_template_id] for mail_template_id in activity['mail_template_ids']]
        return activities



class ResUsers(models.Model):
    _inherit = 'res.users'

    @api.model
    def systray_get_activities(self):
        activities = super(ResUsers, self).systray_get_activities()
        return activities

class MergePartnerAutomaticCustom(models.TransientModel):
    _inherit='base.partner.merge.automatic.wizard'


    def _merge(self, partner_ids, dst_partner=None, extra_checks=True):
            """ private implementation of merge partner
                :param partner_ids : ids of partner to merge
                :param dst_partner : record of destination res.partner
                :param extra_checks: pass False to bypass extra sanity check (e.g. email address)
            """
            # super-admin can be used to bypass extra checks
            if self.env.is_admin():
                extra_checks = False

            Partner = self.env['res.partner']
            partner_ids = Partner.browse(partner_ids).exists()
            if len(partner_ids) < 2:
                return

            if len(partner_ids) > 3:
                raise UserError(_("For safety reasons, you cannot merge more than 3 contacts together. You can re-open the wizard several times if needed."))

            # check if the list of partners to merge contains child/parent relation
            child_ids = self.env['res.partner']
            for partner_id in partner_ids:
                child_ids |= Partner.search([('id', 'child_of', [partner_id.id])]) - partner_id
            if partner_ids & child_ids:
                raise UserError(_("You cannot merge a contact with one of his parent."))

            if extra_checks and len(set(partner.email for partner in partner_ids)) > 1:
                raise UserError(_("All contacts must have the same email. Only the Administrator can merge contacts with different emails."))

            # remove dst_partner from partners to merge
            if dst_partner and dst_partner in partner_ids:
                src_partners = partner_ids - dst_partner
            else:
                ordered_partners = self._get_ordered_partner(partner_ids.ids)
                dst_partner = ordered_partners[-1]
                src_partners = ordered_partners[:-1]
            _logger.info("dst_partner: %s", dst_partner.id)

            # FIXME: is it still required to make and exception for account.move.line since accounting v9.0 ?
            if extra_checks and 'account.move.line' in self.env and self.env['account.move.line'].sudo().search([('partner_id', 'in', [partner.id for partner in src_partners])]):
                raise UserError(_("Only the destination contact may be linked to existing Journal Items. Please ask the Administrator if you need to merge several contacts linked to existing Journal Items."))

            # Make the company of all related users consistent with destination partner company
            if dst_partner.company_id:
                partner_ids.mapped('user_ids').sudo().write({
                    'company_ids': [Command.link(dst_partner.company_id.id)],
                    'company_id': dst_partner.company_id.id
                })

            #--------------------------------
            #CUSTOM CHANGES
            #--------------------------------

            if dst_partner.activity_ids:
                for activity in dst_partner.activity_ids:
                    activity.res_id = dst_partner.id
            if src_partners.activity_ids:
                for activity in src_partners.activity_ids:
                    activity.res_id = dst_partner.id


            # call sub methods to do the merge
            self._update_foreign_keys(src_partners, dst_partner)
            # self._update_reference_fields(src_partners, dst_partner)
            self._update_values(src_partners, dst_partner)

            self._log_merge_operation(src_partners, dst_partner)

            # delete source partner, since they are merged
            src_partners.unlink()