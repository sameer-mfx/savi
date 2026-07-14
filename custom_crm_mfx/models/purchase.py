from odoo import api, models, fields, _


class PurchaseOrder(models.Model):
    _inherit = 'purchase.order'

    tandc_id = fields.Many2one(comodel_name='def.tandc', string='Terms and Conditions')
    sale_order_ids = fields.Many2many(comodel_name='sale.order', string='Sale Orders')
    partner_email = fields.Char(related='partner_id.email', string='Email', readonly=False, store=True)
    partner_mobile = fields.Char(related='partner_id.mobile', string='Mobile', readonly=False, store=True)

    @api.onchange('tandc_id')
    def fill_terms_and_conditions_in_po(self):
        for rec in self:
            if rec.tandc_id:
                rec.notes = rec.tandc_id.terms_and_conditions
            else:
                rec.notes = ''

    def button_cancel(self):
        res = super().button_cancel()
        if self.env.context.get('skip_cancel_email'):
            return res
        orders_to_notify = self.filtered(lambda o: o.partner_id and o.state == 'cancel')
        if len(orders_to_notify) == 1:
            return orders_to_notify._action_open_cancel_email_wizard()
        for order in orders_to_notify:
            order._send_cancel_email_auto()
        return res

    def _action_open_cancel_email_wizard(self):
        self.ensure_one()
        template = self.env.ref(
            'custom_crm_mfx.email_template_purchase_cancel', raise_if_not_found=False
        )
        compose_form = self.env.ref(
            'mail.email_compose_message_wizard_form', raise_if_not_found=False
        )
        ctx = {
            'default_model': 'purchase.order',
            'default_res_ids': self.ids,
            'default_template_id': template.id if template else False,
            'default_composition_mode': 'comment',
            'default_email_layout_xmlid': 'mail.mail_notification_layout_with_responsible_signature',
            'mark_po_as_sent': False,
            'force_email': True,
        }
        return {
            'name': _('Send PO Cancellation'),
            'type': 'ir.actions.act_window',
            'view_mode': 'form',
            'res_model': 'mail.compose.message',
            'views': [(compose_form.id, 'form')] if compose_form else False,
            'view_id': compose_form.id if compose_form else False,
            'target': 'new',
            'context': ctx,
        }

    def _send_cancel_email_auto(self):
        self.ensure_one()
        template = self.env.ref(
            'custom_crm_mfx.email_template_purchase_cancel', raise_if_not_found=False
        )
        if not template:
            return
        template.with_context(force_send=True).send_mail(
            self.id, force_send=True,
            email_layout_xmlid='mail.mail_notification_layout_with_responsible_signature',
        )
