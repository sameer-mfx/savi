from odoo import fields, models


class ResConfigSettings(models.TransientModel):
    _inherit = "res.config.settings"

    savi_lead_ack_email_enabled = fields.Boolean(
        string="Send enquiry acknowledgement emails",
        config_parameter="savi_message_automation.lead_ack_email_enabled",
    )
    savi_dispatch_customer_email_enabled = fields.Boolean(
        string="Send dispatch update emails",
        config_parameter="savi_message_automation.dispatch_customer_email_enabled",
    )
    savi_service_assignment_activity_enabled = fields.Boolean(
        string="Create engineer assignment activities",
        config_parameter="savi_message_automation.service_assignment_activity_enabled",
    )
    savi_service_assignment_customer_email_enabled = fields.Boolean(
        string="Send service assignment emails",
        config_parameter="savi_message_automation.service_assignment_customer_email_enabled",
    )
    savi_srn_feedback_email_enabled = fields.Boolean(
        string="Auto-send SRN feedback emails",
        config_parameter="savi_message_automation.srn_feedback_email_enabled",
    )
    savi_amc_renewal_activity_enabled = fields.Boolean(
        string="Create AMC renewal activities",
        config_parameter="savi_message_automation.amc_renewal_activity_enabled",
    )
    savi_amc_renewal_customer_email_enabled = fields.Boolean(
        string="Send AMC renewal emails",
        config_parameter="savi_message_automation.amc_renewal_customer_email_enabled",
    )
    savi_amc_renewal_days = fields.Integer(
        string="AMC renewal reminder days",
        config_parameter="savi_message_automation.amc_renewal_days",
        default=30,
    )
