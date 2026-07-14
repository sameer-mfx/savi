from odoo import models, fields, api

class ProjectStage(models.Model):
    _inherit = 'project.project.stage'

    is_final_stage = fields.Boolean(
        string="Is Final Stage",
        default=False,
        help="If checked, this stage will be considered the final stage globally. "
             "Only one stage can be marked as final in the entire system."
    )

    @api.model
    def create(self, vals):
        record = super().create(vals)
        if vals.get('is_final_stage'):
            record._unset_other_final_stages()
        return record

    def write(self, vals):
        res = super().write(vals)
        if vals.get('is_final_stage'):
            for stage in self:
                if stage.is_final_stage:
                    stage._unset_other_final_stages()
        return res

    def _unset_other_final_stages(self):
        """Unset 'is_final_stage' for all other stages globally."""
        other_stages = self.search([('id', '!=', self.id), ('is_final_stage', '=', True)])
        if other_stages:
            other_stages.write({'is_final_stage': False})