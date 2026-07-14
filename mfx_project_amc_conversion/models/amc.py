from odoo import models, fields, api

class AMC(models.Model):
    _inherit = 'amc.order'

    project_id = fields.Many2one(comodel_name='project.project')