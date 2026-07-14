from odoo import models, fields, api, _
from odoo.exceptions import UserError


class AmcVisitWizard(models.TransientModel):
    _name = 'amc.visit.wizard'
    _description = 'Create AMC Visit Wizard'

    amc_order_id = fields.Many2one('amc.order', string='AMC Order', required=True, readonly=True)
    partner_id = fields.Many2one(related='amc_order_id.partner_id', string='Customer', readonly=True)
    assigned_to_ids = fields.Many2many('res.users', string='Assign Engineers', required=True)
    visit_date = fields.Datetime(string='Visit Date', required=True)
    remarks = fields.Text(string='Remarks / Instructions for Engineer')
    wizard_line_ids = fields.One2many('amc.visit.wizard.line', 'wizard_id', string='AMC Lines')

    @api.model
    def default_get(self, fields_list):
        res = super().default_get(fields_list)
        active_id = self.env.context.get('active_id')
        if active_id:
            amc_order = self.env['amc.order'].browse(active_id)
            res['amc_order_id'] = amc_order.id
            lines = []
            for line in amc_order.amc_lines_ids:
                if line.is_tracked and line.product_identification_ids:
                    # One wizard line per serial number for tracked products
                    for lot in line.product_identification_ids:
                        lines.append((0, 0, {
                            'amc_line_id': line.id,
                            'lot_id': lot.id,
                            'selected': False,
                        }))
                else:
                    # One wizard line for non-tracked products
                    lines.append((0, 0, {
                        'amc_line_id': line.id,
                        'selected': False,
                    }))
            res['wizard_line_ids'] = lines
        return res

    def action_create_visit(self):
        self.ensure_one()
        selected_lines = self.wizard_line_ids.filtered(lambda l: l.selected)
        if not selected_lines:
            raise UserError(_("Please select at least one AMC line item for the visit."))

        amc_order = self.amc_order_id
        if amc_order.is_amc_expired:
            raise UserError(_("You cannot create a visit for an expired AMC Order."))

        # Group selected wizard lines by AMC line to combine serials
        amc_line_map = {}
        for wiz_line in selected_lines:
            amc_line = wiz_line.amc_line_id
            if amc_line.id not in amc_line_map:
                amc_line_map[amc_line.id] = {
                    'amc_line': amc_line,
                    'lot_ids': [],
                    'location': wiz_line.location,
                }
            if wiz_line.lot_id:
                amc_line_map[amc_line.id]['lot_ids'].append(wiz_line.lot_id.id)

        visit_lines = []
        for data in amc_line_map.values():
            amc_line = data['amc_line']
            visit_line = self.env['amc.site.visit.line'].create({
                'product_id': amc_line.product_id.id,
                'service_id': amc_line.service_id.id,
                'description': amc_line.description,
                'amc_order_line_id': amc_line.id,
                'product_identification_ids': [(6, 0, data['lot_ids'])],
                'company_id': amc_line.company_id.id,
                'location': data['location'],
            })
            visit_lines.append(visit_line)

        visit_vals = {
            'assigned_by': self.env.user.id,
            'engineer_ids': [(6, 0, self.assigned_to_ids.ids)],
            'partner_id': amc_order.partner_id.id,
            'partner_address': amc_order.partner_address,
            'partner_email': amc_order.partner_email,
            'partner_phone': amc_order.partner_phone,
            'company_id': amc_order.company_id.id,
            'amc_order_id': amc_order.id,
            'visit_line_ids': [(4, line.id) for line in visit_lines],
            'state': 'draft',
            'date_order': self.visit_date,
            'note': self.remarks,
        }
        visit = self.env['amc.site.visit'].create(visit_vals)
        amc_order.amc_site_visit_ids += visit

        return {
            'type': 'ir.actions.act_window',
            'name': _('AMC Visit'),
            'res_model': 'amc.site.visit',
            'res_id': visit.id,
            'view_mode': 'form',
            'target': 'current',
        }


class AmcVisitWizardLine(models.TransientModel):
    _name = 'amc.visit.wizard.line'
    _description = 'AMC Visit Wizard Line'

    wizard_id = fields.Many2one('amc.visit.wizard', string='Wizard', ondelete='cascade')
    amc_line_id = fields.Many2one('amc.order.lines', string='AMC Line', required=True)
    selected = fields.Boolean(string='Select', default=False)
    product_id = fields.Many2one(related='amc_line_id.product_id', string='Product')
    service_id = fields.Many2one(related='amc_line_id.service_id', string='Service')
    description = fields.Char(related='amc_line_id.description', string='Description')
    location = fields.Char(related='amc_line_id.location', string='Location')
    lot_id = fields.Many2one('stock.lot', string='Serial Number')
