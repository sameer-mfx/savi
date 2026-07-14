from odoo import models, fields, api, _
from odoo.exceptions import UserError
from collections import defaultdict

class Project(models.Model):
    _inherit = 'project.project'

    is_project_done = fields.Boolean(string="Final Stage of Project", default=False, compute='_compute_is_project_done')
    amc_id = fields.Many2one('amc.order', string="AMC")

    @api.depends('stage_id')
    def _compute_is_project_done(self):
        for project in self:
            project.is_project_done = project.stage_id.is_final_stage

    def convert_project_to_amc(self):
        """Validate stage, build AMC wizard grouped by product+location, open wizard popup."""
        self.ensure_one()

        if not self.is_project_done:
            raise UserError(_("Project is not in final stage"))

        Wizard = self.env['project.amc.wizard']
        WizardLine = self.env['project.amc.wizard.line']

        # Create wizard header record
        wizard = Wizard.create({
            'project_id': self.id,
            'partner_id': getattr(self, 'partner_id', False) and self.partner_id.id or False,
            'company_id': self.company_id.id,
            'currency_id': self.company_id.currency_id.id,
        })

        # fields to collect items from
        task_item_fields = [
            'audio_task_items_ids',
            'video_task_items_ids',
            'video_conferencing_task_items_ids',
            'controller_task_items_ids',
            'switching_task_items_ids',
            'accessories_task_items_ids',
        ]

        # Group by (product_id, location)
        grouped = defaultdict(lambda: {
            'quantity': 0.0,
            'product_identifications': set(),
            'description': '',
        })

        for task in self.task_ids:
            for field_name in task_item_fields:
                if not hasattr(task, field_name):
                    continue
                for item in getattr(task, field_name):
                    product = item.product_id
                    if not product:
                        continue
                    key = (product.id, task.name)

                    # description: keep first non-empty
                    desc = ''
                    if hasattr(item, 'description') and item.description:
                        desc = item.description
                    elif product:
                        desc = product.display_name

                    entry = grouped[key]
                    entry['quantity'] += getattr(item, 'quantity', 1.0)
                    entry['product_identifications'].update(item.product_identification_ids.ids)
                    if not entry['description']:
                        entry['description'] = desc

        # Create wizard lines for each grouped key
        for (product_id, location), values in grouped.items():
            WizardLine.create({
                'amc_wizard_id': wizard.id,
                'product_id': product_id,
                'description': values['description'],
                'product_identification_ids': [(6, 0, list(values['product_identifications']))],
                'location': location,
                'company_id': wizard.company_id.id,
            })

        return {
            'type': 'ir.actions.act_window',
            'name': _('Convert Project to AMC'),
            'res_model': 'project.amc.wizard',
            'view_mode': 'form',
            'view_id': self.env.ref('mfx_project_amc_conversion.project_amc_wizard_form_view').id,
            'res_id': wizard.id,
            'target': 'new',
        }

    def action_view_amcs(self):
        return {
            'type': 'ir.actions.act_window',
            'name': _('AMCs'),
            'res_model': 'amc.order',
            'view_mode': 'form',
            'res_id': self.amc_id.id,
            'target': 'current',
        }