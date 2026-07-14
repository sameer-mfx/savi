from odoo import models, fields, api, _


class ProjectTaskType(models.Model):
    _inherit = 'project.task.type'

    can_add_products_to_so = fields.Boolean(
        string='Can Add Products',
        default=False,
        help="If checked, this stage allows adding products to the sales order for tasks in this project."
    )

    @api.model
    def create(self, vals):
        record = super().create(vals)
        if vals.get('can_add_products_to_so'):
            record._unset_other_stages(record.project_ids)
        return record

    def write(self, vals):
        res = super().write(vals)
        if vals.get('can_add_products_to_so'):
            for stage in self:
                if stage.can_add_products_to_so:
                    stage._unset_other_stages(stage.project_ids)
        return res

    def _unset_other_stages(self, projects):
        """Unset 'can_add_products_to_so' for all other stages in the same projects."""
        for project in projects:
            other_stages = project.type_ids.filtered(lambda s: s.id != self.id and s.can_add_products_to_so)
            if other_stages:
                other_stages.write({'can_add_products_to_so': False})