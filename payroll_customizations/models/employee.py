from odoo import models, fields

class HrEmployee(models.Model):
    _inherit = 'hr.employee'

    employee_code = fields.Char(string='Employee Code')  # Avoid name conflict with technical ID
    pan = fields.Char(string='PAN')
    aadhar_no = fields.Char(string='Aadhar Number')
    uan_no = fields.Char(string='UAN Number')
    esic_no = fields.Char(string='ESIC Number')
    date_of_joining = fields.Date(string='Date of Joining')
    date_of_releaving = fields.Date(string='Date of Releaving')