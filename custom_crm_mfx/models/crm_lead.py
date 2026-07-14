from odoo import api, fields, models, _
from odoo.exceptions import UserError

class CrmLead(models.Model):
    _inherit = 'crm.lead'

    visit_form_ids = fields.One2many(comodel_name='crm.visit.form', inverse_name='crm_lead_id')
    lead_owner = fields.Many2one(comodel_name='res.users', string='Lead Owner')
    sales_coordinator = fields.Many2one(comodel_name='res.users', string='Sales Coordinator')

document_mimetypes = ['application/msword', 'application/vnd.openxmlformats-officedocument.wordprocessingml.document']
presentation_mimetypes = ['application/vnd.ms-powerpoint', 'application/vnd.openxmlformats-officedocument.presentationml.presentation']
spreadsheet_mimetypes = ['application/vnd.ms-excel', 'application/vnd.openxmlformats-officedocument.spreadsheetml.sheet']
drawing_mimetypes = ['application/acad', 'image/svg+xml', 'application/octet-stream']
pdf_mimetypes = ['application/pdf']
image_mimetypes = ['image/jpeg', 'image/png', 'image/jpg', 'image/webp', 'image/gif']
video_mimetypes = ['video/mp4', 'video/quicktime', 'video/x-msvideo', 'video/x-matroska', 'video/webm', 'video/x-flv']

class CrmVisitForm(models.Model):
    _name = 'crm.visit.form'

    crm_lead_id = fields.Many2one(comodel_name='crm.lead')
    sales_person_id = fields.Many2one(comodel_name='res.users', related='crm_lead_id.user_id')
    date_of_visit = fields.Date(string='Date of site visit', required=True)
    client_id = fields.Many2one(comodel_name='res.partner', related='crm_lead_id.partner_id')
    client_representative_id = fields.Many2one(comodel_name='res.partner', string='Client Representative Name', domain="[('parent_id', '=', client_id)]")
    client_mobile = fields.Char(string='Client Mobile Number', related='client_representative_id.mobile')
    client_email = fields.Char(string='Client Email ID', related='client_representative_id.email')
    client_address = fields.Char(string='Full address of the client location')
    room_name = fields.Char(string='Room Name')
    room_length = fields.Integer(string='Room Length (Feet)')
    room_width = fields.Integer(string='Room Width (Feet)')
    room_height = fields.Integer(string='Room Height (Feet)')
    ceiling_type = fields.Char(string='Ceiling Type')
    ceiling_height = fields.Integer(string='Ceiling Height (Feet)')
    wall_material = fields.Char(string='Wall Material')
    floor_type = fields.Char(string='Flooring Type')
    mounting_surface_details = fields.Char(string='Mounting Surface Details')
    ambient_light_condition = fields.Char(string='Ambient Light Condition')
    display_system = fields.Char(string='Display System', help='Size, Type(LED/LCD/Projection), Quantity')
    audio_req = fields.Char(string='Audio Requirement')
    control_system = fields.Char(string='Control System', help='Any Specific control brand or preference')
    video_conferencing_system = fields.Char(string='Video Conferencing System', help='Type (Zoom/Teams/Cisco), camera specs')
    light_integration = fields.Selection(selection=[('yes', 'Yes'), ('no', 'No')], string='Light Integration', help='If any automation/integration needed')
    equipment_room = fields.Char(string='Equipment Room', help='Dedicated area or shared space')
    cabling_pathways = fields.Char(string='Cabling & Conduit Pathways', help='Existing or proposed pathways')
    internet_facilities = fields.Char(string='Internet Facilities', help='LAN Ports, WiFi, Internet Availability')
    power_availability = fields.Char(string='Power Availability', help='Power sources, UPS needed, load available')
    hvac_acoustics = fields.Char(string='HVAC/Acoustics', help='Any constraints or expectations')
    site_images = fields.Many2many(comodel_name='ir.attachment', relation='crm_site_images_rel', domain=[('res_model', '=', 'crm.visit.form')], string='Upload Site Images', help='Upload clear images of the room/site')
    site_videos = fields.Many2many(comodel_name='ir.attachment', relation='crm_site_videos_rel', domain=[('res_model', '=', 'crm.visit.form')], string='Upload Site Videos', help='Short videos showing 360° view')
    floor_plan = fields.Many2many(comodel_name='ir.attachment', relation='crm_floor_plan_image_rel', domain=[('res_model', '=', 'crm.visit.form')], string='Upload Floor Plan (if any)', help='PDF/DWG/JPG formats accepted')
    client_docs = fields.Many2many(comodel_name='ir.attachment', relation='crm_client_docs_images_rel', domain=[('res_model', '=', 'crm.visit.form')], string='Upload Client Shared Docs', help='BOQ, RFP, previous designs if any')
    client_expectations = fields.Char(string='Client Expectations', help='Key points the client wants from the AV system')
    challenges_observed = fields.Char(string='Challenges Observed', help='Eg. Site-level issues (access, space, acoustics, etc.)')
    recommendations = fields.Char(string='Recommendations', help='Suggestions or ideas for AV setup')
    actions_planned = fields.Char(string='Next Steps / Actions Planned', help='Follow-ups, demo planning, design submission, etc.')

    @api.onchange('site_images', 'site_videos', 'floor_plan', 'client_docs')
    def _check_attachment_constrains(self):
        for rec in self:
            for attachment in rec.site_images:
                if attachment.mimetype not in pdf_mimetypes + image_mimetypes:
                    raise UserError("Site Images must be in PDF, JPG, PNG, or SVG formats.")

            for attachment in rec.site_videos:
                if attachment.mimetype not in video_mimetypes:
                    raise UserError("Only MP4 videos are allowed in Site Videos.")

            for attachment in rec.floor_plan:
                if attachment.mimetype not in drawing_mimetypes + pdf_mimetypes + image_mimetypes:
                    raise UserError("Floor Plans must be in PDF, JPG, PNG, SVG, or DWG formats.")

            for attachment in rec.client_docs:
                if attachment.mimetype not in document_mimetypes + presentation_mimetypes + spreadsheet_mimetypes + drawing_mimetypes + pdf_mimetypes + image_mimetypes:
                    raise UserError("Client Documents must be a Document, Presentation, Spreadsheet, Drawing, PDF, or Image file.")

    @api.onchange('date_of_visit')
    def _check_date_of_visit(self):
        for rec in self:
            if rec.date_of_visit and rec.date_of_visit < fields.Date.today():
                raise UserError(_("Date of site visit cannot be in Past Dates"))