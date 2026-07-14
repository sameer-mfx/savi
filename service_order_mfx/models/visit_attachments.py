from odoo import models, fields, api, exceptions, _

def get_google_maps_url(latitude, longitude):
    return "https://maps.google.com?q=%s,%s" % (latitude, longitude)

class ServiceOrder(models.Model):
    _inherit = 'service.order'

    check_in_image = fields.Many2many(comodel_name='ir.attachment', relation='service_order_check_in_image_rel', domain=[('res_model', '=', 'service.order')], string='Site - Check In Image', copy=False)
    check_out_image = fields.Many2many(comodel_name='ir.attachment', relation='service_order_check_out_image_rel', domain=[('res_model', '=', 'service.order')], string='Site - Check Out Image', copy=False)
    check_in_time = fields.Datetime(string='Check In Time', copy=False)
    check_in_latitude = fields.Float()
    check_in_longitude = fields.Float()
    check_out_time = fields.Datetime(string='Check Out Time', copy=False)
    check_out_latitude = fields.Char()
    check_out_longitude = fields.Char()
    customer_feedback = fields.Html(string='Customer Feedback', copy=False)
    customer_rating = fields.Selection(selection=[(str(i), str(i)) for i in range(6)], string='Customer Rating', copy=False)

    def action_check_in(self):
        for order in self:
            order.check_in_time = fields.Datetime.now()

    def action_check_out(self):
        for order in self:
            order.check_out_time = fields.Datetime.now()

    @api.model_create_multi
    def create(self, vals_list):
        records = super().create(vals_list)
        records._update_attachment_res_model()
        return records

    def write(self, vals):
        result = super().write(vals)
        if 'check_in_image' in vals or 'check_out_image' in vals:
            self._update_attachment_res_model()
        return result

    def _update_attachment_res_model(self):
        """Update res_model and res_id for attachments linked to check-in/check-out images"""
        Attachment = self.env['ir.attachment'].sudo()
        for order in self:
            if order.check_in_image:
                attachments = Attachment.browse(order.check_in_image.ids)
                attachments.filtered(lambda a: not a.res_model or a.res_model != 'service.order').write({
                    'res_model': 'service.order',
                    'res_id': order.id,
                })
            if order.check_out_image:
                attachments = Attachment.browse(order.check_out_image.ids)
                attachments.filtered(lambda a: not a.res_model or a.res_model != 'service.order').write({
                    'res_model': 'service.order',
                    'res_id': order.id,
                })

    @api.constrains('check_in_time', 'check_out_time')
    def _check_validity_check_in_check_out(self):
        """ verifies if check_in is earlier than check_out. """
        for rec in self:
            if rec.check_in_time and rec.check_out_time:
                if rec.check_out_time < rec.check_in_time:
                    raise exceptions.ValidationError(_('"Check Out" time cannot be earlier than "Check In" time.'))

    def action_in_attendance_maps(self):
        self.ensure_one()
        return {
            'type': 'ir.actions.act_url',
            'url': get_google_maps_url(self.check_in_latitude, self.check_in_longitude),
            'target': 'new'
        }

    def action_out_attendance_maps(self):
        self.ensure_one()
        return {
            'type': 'ir.actions.act_url',
            'url': get_google_maps_url(self.check_out_latitude, self.check_out_longitude),
            'target': 'new'
        }