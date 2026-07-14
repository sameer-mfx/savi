from odoo import api, fields, models, _

class HrPayslipLine(models.Model):
    _inherit = 'hr.payslip.line'

    emp_name = fields.Char(
        string='Employee Name',
        related='employee_id.name',
        store=True
    )

    emp_id = fields.Char(
        string='Employee ID',
        related='employee_id.employee_code',
        store=True
    )
    designation = fields.Char(
        string='Designation',
        related='employee_id.job_id.name',
        store=True
    )
    department = fields.Char(
        string='Department',
        related='employee_id.department_id.name',
        store=True
    )
    emp_work_location = fields.Char(
        string='Location',
        related='employee_id.work_location_id.name',
        store=True
    )
    emp_bank_account_no = fields.Char(
        string='Bank A/C No',
        related='employee_id.bank_account_id.acc_number',
        store=True
    )

    # employee_id = fields.Many2one('hr.payslip.worked.days', string='Employee',
    #                               required=True,
    #                               help="Choose Employee for line")
    #

    # work_days = fields.Char(
    #     string='Work Days',
    #     related='slip_id.worked_days_line_ids.number_of_days',
    #     store=True
    # )

    # days_present = fields.Float(string='Days Present', compute='_compute_days_present', store=True)
    #
    # @api.depends('slip_id.worked_days_line_ids')
    # def _compute_days_present(self):
    #     for line in self:
    #         # Example: Sum all "Worked Days" entries (you can filter by name, code, or other criteria)
    #         worked_days = line.slip_id.worked_days_line_ids.filtered(
    #             lambda wd: wd.code == 'WORK100' or wd.name.lower() == 'worked days'
    #         )
    #         line.days_present = sum(worked_days.mapped('number_of_days')) if worked_days else 0.0

    pan = fields.Char(
        string='PAN',
        related='employee_id.pan',
        store=True
    )
    aadhar_no = fields.Char(
        string='Aadhar Number',
        related='employee_id.aadhar_no',
        store=True
    )
    uan_no = fields.Char(
        string='UAN Number',
        related='employee_id.uan_no',
        store=True
    )
    esic_no = fields.Char(
        string='ESIC Number',
        related='employee_id.esic_no',
        store=True
    )
    date_of_joining = fields.Date(
        string='Date of Joining',
        related='employee_id.date_of_joining',
        store=True
    )
    # date_of_releaving = fields.Date(
    #     string='Date of Releaving',
    #     related='employee_id.date_of_releaving',
    #     store=True
    # )


    currency_id = fields.Many2one(
        'res.currency',
        string="Currency",
        related='employee_id.contract_id.currency_id',
        store=True
    )

    emp_basic_salary = fields.Monetary(
        string='Basic Salary',
        related='employee_id.contract_id.wage',
        currency_field='currency_id',
        store=True
    )
    emp_hra = fields.Monetary(
        string='HRA',
        related='employee_id.contract_id.hra',
        currency_field='currency_id',
        store=True
    )
    emp_conveyance_allowance = fields.Monetary(
        string='Conveyance Allowance',
        related='employee_id.contract_id.conveyance_allowance',
        currency_field='currency_id',
        store=True
    )
    emp_medical_allowance = fields.Monetary(
        string='Medical Allowance',
        related='employee_id.contract_id.medical_allowance',
        currency_field='currency_id',
        store=True
    )
    emp_special_allowance = fields.Monetary(
        string='Special Allowance',
        related='employee_id.contract_id.special_allowance',
        currency_field='currency_id',
        store=True
    )
    emp_other_allowance = fields.Monetary(
        string='Other Allowance',
        related='employee_id.contract_id.other_allowance',
        currency_field='currency_id',
        store=True
    )
    emp_overtime = fields.Monetary(
        string='Overtime',
        related='employee_id.contract_id.over_time',
        currency_field='currency_id',
        store=True
    )
    emp_incentives = fields.Monetary(
        string='Incentives',
        related='employee_id.contract_id.incentives',
        currency_field='currency_id',
        store=True
    )
    emp_bonus = fields.Monetary(
        string='Bonus',
        related='employee_id.contract_id.bonus',
        currency_field='currency_id',
        store=True
    )
    emp_gross = fields.Monetary(
        string='Gross',
        related='employee_id.contract_id.gross',
        currency_field='currency_id',
        store=True
    )
    emp_pf = fields.Monetary(
        string='PF Employee Contribution',
        related='employee_id.contract_id.pf_employee_contribution',
        currency_field='currency_id',
        store=True
    )
    emp_esic = fields.Monetary(
        string='ESIC Employee Contribution',
        related='employee_id.contract_id.esic_employee_contribution',
        currency_field='currency_id',
        store=True
    )
    emp_prof_tax = fields.Monetary(
        string='Professional Tax',
        related='employee_id.contract_id.professional_tax',
        currency_field='currency_id',
        store=True
    )
    emp_inc_tax = fields.Monetary(
        string='Income Tax',
        related='employee_id.contract_id.income_tax',
        currency_field='currency_id',
        store=True
    )
    emp_adv_loan_deduction = fields.Monetary(
        string='Advance/Loan Deduction',
        related='employee_id.contract_id.advance_loan_deduction',
        currency_field='currency_id',
        store=True
    )
    emp_other_deductions = fields.Monetary(
        string='Other Deductions',
        related='employee_id.contract_id.other_deductions',
        currency_field='currency_id',
        store=True
    )

    emp_total_deductions = fields.Monetary(
        string='Total Deductions',
        related='employee_id.contract_id.total_deductions',
        currency_field='currency_id',
        store=True
    )

    emp_net_salary = fields.Monetary(
        string='Net Salary',
        related='employee_id.contract_id.net_salary',
        currency_field='currency_id',
        store=True
    )

    employer_pf_contribution = fields.Monetary(
        string='Employer PF Contribution',
        related='employee_id.contract_id.employer_pf_contribution',
        currency_field='currency_id',
        store=True
    )

    employer_esic_contribution = fields.Monetary(
        string='Employer ESIC Contribution',
        related='employee_id.contract_id.employer_esic_contribution',
        currency_field='currency_id',
        store=True
    )

    remarks = fields.Text(
        string='Remarks',
        related='employee_id.contract_id.remarks',
        currency_field='currency_id',
        store=True
    )

    work_days_in_month = fields.Float(
        string="Work Days in Month",
        related='employee_id.contract_id.work_days_in_month',
        store=True
    )
    days_present = fields.Float(
        string="Days Present",
        related='employee_id.contract_id.days_present',
        store=True
    )
    lop_days = fields.Float(
        string="LOP Days",
        related='employee_id.contract_id.lop_days',
        store=True
    )