from odoo import models, fields, api, _
from odoo.exceptions import UserError
from dateutil.relativedelta import relativedelta

class ProjectAMCWizard(models.TransientModel):
    _name = "project.amc.wizard"
    _description = "Project AMC Wizard"

    user_id = fields.Many2one(comodel_name='res.users', string='User', required=True, default=lambda self: self.env.user)
    partner_id = fields.Many2one(comodel_name='res.partner', string='Customer', required=True)
    company_id = fields.Many2one(comodel_name='res.company', string='Company', default=lambda self: self.env.user.company_id.id)
    currency_id = fields.Many2one(comodel_name='res.currency', string='Currency', required=True, default=lambda self: self.env.user.company_id.currency_id.id)
    amc_start_date = fields.Date(string='AMC Start Date', default=lambda self: fields.Date.context_today(self))
    amc_duration = fields.Integer(string='AMC Duration', default=1)
    amc_duration_unit = fields.Selection(selection=[('month', 'Month'), ('year', 'Year')], string='Duration Type')
    amc_end_date = fields.Date(string='AMC End Date')
    project_id = fields.Many2one(comodel_name='project.project', string='Project', required=True)
    amc_wizard_line_ids = fields.One2many(comodel_name='project.amc.wizard.line', inverse_name='amc_wizard_id', string='AMC Wizard Lines')

    @api.onchange('amc_start_date', 'amc_duration', 'amc_duration_unit')
    def _onchange_amc_dates(self):
        today = fields.Date.today()
        if self.amc_start_date and self.amc_start_date < today:
            raise UserError('AMC Start Date must be greater than or equal to today')
        if self.amc_start_date and self.amc_duration and self.amc_duration_unit:
            start_date = fields.Date.from_string(self.amc_start_date)
            if self.amc_duration_unit == 'year':
                end_date = start_date + relativedelta(years=self.amc_duration) - relativedelta(days=1)
            else:
                end_date = start_date + relativedelta(months=self.amc_duration) - relativedelta(days=1)
            self.amc_end_date = end_date
        else:
            self.amc_end_date = False

    def action_confirm(self):
        """Create AMC Order and its lines from wizard data."""
        self.ensure_one()

        # Create AMC Order (assuming your model is 'amc.order')
        amc_order = self.env['amc.order'].create({
            'partner_id': self.partner_id.id,
            'amc_start_date': self.amc_start_date,
            'amc_duration': self.amc_duration,
            'amc_duration_unit': self.amc_duration_unit,
            'amc_end_date': self.amc_end_date,
            'project_id': self.project_id.id,
            'company_id': self.company_id.id,
            'currency_id': self.currency_id.id,
            # add any other fields your amc.order model requires
        })

        # Create AMC Order Lines from wizard lines (if your amc.order has lines)
        for line in self.amc_wizard_line_ids:
            if not line.service_id:
                raise UserError('Please select Service in line with product - %s' % line.product_id.name)
            self.env['amc.order.lines'].create({
                'amc_id': amc_order.id,
                'product_id': line.product_id.id,
                'service_id': line.service_id.id,
                'description': line.description,
                'is_tracked': True if line.product_id.tracking != 'none' else False,
                'product_identification_ids': [(6, 0, line.product_identification_ids.ids)],
                'quantity': len(line.product_identification_ids.ids) if line.product_identification_ids else 1,
                'location': line.location,
                'company_id': line.company_id.id,
                # add other fields as needed
            })
        self.project_id.amc_id = amc_order.id

        # Return the newly created AMC Order in form view
        return {
            'type': 'ir.actions.act_window',
            'name': _('AMC Order'),
            'res_model': 'amc.order',
            'view_mode': 'form',
            'res_id': amc_order.id,
            'target': 'current',
        }

class ProjectAMCWizardLine(models.TransientModel):
    _name = "project.amc.wizard.line"
    _description = "Project AMC Wizard Line"

    amc_wizard_id = fields.Many2one(comodel_name='project.amc.wizard', string='AMC Wizard', required=True)
    product_id = fields.Many2one(comodel_name='product.product', string='Product', domain="[('detailed_type', '!=', 'service')]", required=True)
    service_id = fields.Many2one(comodel_name='amc.services', string='Service Name')
    description = fields.Char('Description')
    product_identification_ids = fields.Many2many(comodel_name='stock.lot', string='Identification Numbers', copy=False)
    location = fields.Char(string='Location')
    company_id = fields.Many2one(comodel_name='res.company', string='Company', default=lambda self: self.env.user.company_id.id)

    @api.onchange('service_id')
    def _onchange_service_id(self):
        if self.service_id:
            self.description = self.service_id.description