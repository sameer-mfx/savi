# -*- coding: utf-8 -*-
# Copyright (C) Softhealer Technologies.

from odoo import api,fields, models, _
from odoo.exceptions import UserError
from odoo.http import request

FIELD_TYPES = [(key, key) for key in sorted(fields.Field.by_type)]


class ShCreateAction(models.Model):
    _name = 'sh.activity.dynamic.action'
    _description = 'Sh Activity Create Action'

    @api.model
    def _get_model_domain(self):
        models_with_activity = []
        models = self.env['ir.model'].sudo().search([('state', '!=', 'manual')])

        for model in models:
            field_id = self.env['ir.model.fields'].sudo().search([
                ('name', '=', 'activity_ids'),
                ('model_id', '=', model.id),
                ('store', '=', True)
            ], limit=1)
            if field_id:
                models_with_activity.append(model.id)
        return [('id', 'in', models_with_activity)]

    name = fields.Char("Action Name", required=True, index=True)
    model_id = fields.Many2one('ir.model', string='Applies To', required=True, index=True, ondelete='cascade',
                               help="The model this field belongs to",domain=lambda self: self._get_model_domain())

    sh_group_ids = fields.Many2many('res.groups', string='Groups')
    action_id = fields.Many2one(
        'ir.actions.act_window', string="Related Action")

    def add_action_to_model(self):
        if not self.model_id:
            raise UserError(_("Please Select Model."))
        vals = {}
        vals['type'] = 'ir.actions.act_window'
        vals['name'] = self.name
        vals['res_model'] = 'sh.mail.activity'
        vals['binding_model_id'] = self.model_id.id
        vals['binding_type'] = 'action'
        vals['target'] = 'new'
        vals['view_mode'] = 'form'
        vals['domain'] = "[]"
        if self.sh_group_ids:
            vals['groups_id'] = [(6, 0, self.sh_group_ids.ids)]
        action_id = self.env['ir.actions.act_window'].sudo().create(vals)
        self.write({'action_id': action_id.id})

    def remove_action_to_model(self):
        if self.action_id:
            self.action_id.unlink()
