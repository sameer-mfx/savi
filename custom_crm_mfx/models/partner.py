from odoo import api, fields, models
from odoo.exceptions import ValidationError
from datetime import date as dt_date

class Partner(models.Model):
    _inherit = 'res.partner'

    date_of_birth = fields.Date(string='Date of Birth')
    marital_status = fields.Selection(selection=[('single', 'Single'), ('married', 'Married')], string='Marital Status')
    marriage_date = fields.Date(string='Marriage Date')
    formation_date = fields.Date(string='Company Formed On')
    anniversary = fields.Date(string='Anniversary', compute='_compute_anniversary', store=True)
    phone = fields.Char(string='Landline')

    @api.constrains('marriage_date', 'formation_date', 'marital_status')
    def _check_dates(self):
        today = dt_date.today()
        for record in self:
            if record.marital_status == 'married' and record.marriage_date and record.marriage_date > today:
                raise ValidationError("Marriage Date must be in the past for married individuals.")
            if record.formation_date and record.formation_date > today:
                raise ValidationError("Formation Date must be in the past for companies.")

    @api.depends('marriage_date', 'formation_date', 'marital_status')
    def _compute_anniversary(self):
        today = dt_date.today()
        for record in self:
            anniversary_date = False

            # Case 1: Individual with marital status = married
            if record.marital_status == 'married' and record.marriage_date:
                base_date = record.marriage_date

            # Case 2: Company with formation_date
            elif record.formation_date:
                base_date = record.formation_date

            else:
                record.anniversary = False
                continue

            # Calculate next occurrence of the anniversary
            try:
                anniversary_date = dt_date(today.year, base_date.month, base_date.day)
            except ValueError:
                # Handle Feb 29
                anniversary_date = dt_date(today.year, 2, 28)

            if anniversary_date <= today:
                try:
                    anniversary_date = dt_date(today.year + 1, base_date.month, base_date.day)
                except ValueError:
                    anniversary_date = dt_date(today.year + 1, 2, 28)

            record.anniversary = anniversary_date

    @api.model
    def send_anniversary_emails(self):
        today = dt_date.today()
        partners = self.search([('anniversary', '=', today)])
        template = self.env.ref('custom_crm_mfx.email_template_anniversary')
        for partner in partners:
            if template:
                template.send_mail(partner.id, force_send=True)
            partner._compute_anniversary()

    @api.model
    def send_birthday_emails(self):
        today = dt_date.today()
        # Get the month and day for today
        today_month_day = today.strftime('%m-%d')
        # Search for partners whose birthday is today
        partners = self.search([('date_of_birth', '!=', False)])  # Ensure date_of_birth is set
        for partner in partners:
            if partner.date_of_birth.strftime('%m-%d') == today_month_day:
                template = self.env.ref('custom_crm_mfx.email_template_birthday')
                if template:
                    template.send_mail(partner.id, force_send=True)

    def send_bday_mail(self):
        self.send_birthday_emails()

    def send_anv_mail(self):
        self.send_anniversary_emails()