from odoo import api, fields, models, _

class HrContract(models.Model):
    """
    Employee contract based on the visa, work permits
    allows to configure different Salary structure
    """
    _inherit = 'hr.contract'
    _description = 'Employee Contract'

    # currency_id = fields.Many2one(
    #     'res.currency',
    #     string='Currency',
    #     required=True,
    #     default=lambda self: self.env.company.currency_id.id
    # )

    conveyance_allowance = fields.Monetary(string="Conveyance Allowance", help="Conveyance allowance")
    special_allowance = fields.Monetary(string="Special Allowance", help="Special allowance")
    over_time = fields.Monetary(string="Over Time", help="Over Time")
    incentives = fields.Monetary(string="Incentives", help="Incentives")
    bonus = fields.Monetary(string="Bonus", help="Bonus")

    # deductions
    professional_tax = fields.Monetary(string="Professional Tax", help="Professional tax") #, currency_field='currency_id'
    income_tax = fields.Monetary(string="Income Tax (TDS)", help="Income tax (TDS)")
    advance_loan_deduction = fields.Monetary(string="Advance/Loan Deduction", help="Advance or loan deduction",)
    other_deductions = fields.Monetary(string="Other Deductions", help="Other deductions")
    esic_employee_contribution = fields.Monetary(string="ESIC Employee Contribution", help="ESIC employee share")
    pf_employee_contribution = fields.Monetary(string="PF Employee Contribution", help="PF employee share")

    gross = fields.Monetary(
        string='Gross Salary',
        compute='_compute_gross',
        store=True
    )

    @api.depends(
        'wage', 'hra', 'da', 'travel_allowance', 'meal_allowance',
        'medical_allowance', 'other_allowance', 'conveyance_allowance',
        'special_allowance', 'over_time', 'incentives', 'bonus'
    )
    def _compute_gross(self):
        for contract in self:
            contract.gross = sum([
                contract.wage or 0.0,
                contract.hra or 0.0,
                contract.da or 0.0,
                contract.travel_allowance or 0.0,
                contract.meal_allowance or 0.0,
                contract.medical_allowance or 0.0,
                contract.other_allowance or 0.0,
                contract.conveyance_allowance or 0.0,
                contract.special_allowance or 0.0,
                contract.over_time or 0.0,
                contract.incentives or 0.0,
                contract.bonus or 0.0,
            ])

    total_deductions = fields.Monetary(
        string="Total Deductions",
        compute="_compute_total_deductions",
        store=True,
        currency_field='currency_id'
    )

    @api.depends(
        'professional_tax', 'income_tax', 'advance_loan_deduction',
        'other_deductions', 'esic_employee_contribution', 'pf_employee_contribution'
    )
    def _compute_total_deductions(self):
        for contract in self:
            contract.total_deductions = sum([
                contract.professional_tax or 0.0,
                contract.income_tax or 0.0,
                contract.advance_loan_deduction or 0.0,
                contract.other_deductions or 0.0,
                contract.esic_employee_contribution or 0.0,
                contract.pf_employee_contribution or 0.0,
            ])

    net_salary = fields.Monetary(
        string="Net Salary",
        compute="_compute_net_salary",
        store=True,
        currency_field='currency_id'
    )

    @api.depends('gross', 'total_deductions')
    def _compute_net_salary(self):
        for contract in self:
            contract.net_salary = (contract.gross or 0.0) - (contract.total_deductions or 0.0)

    employer_pf_contribution = fields.Monetary(
        string="Employer PF Contribution",
        currency_field='currency_id',
        help="Employer's share of Provident Fund"
    )

    employer_esic_contribution = fields.Monetary(
        string="Employer ESIC Contribution",
        currency_field='currency_id',
        help="Employer's share of ESIC"
    )

    remarks = fields.Text(
        string="Remarks",
        help="Any additional comments or notes regarding the contract"
    )

    work_days_in_month = fields.Float(string="Work Days in Month", help="Total working days in the month")
    days_present = fields.Float(string="Days Present", help="Days employee was present")
    lop_days = fields.Float(string="LOP Days", help="Loss of Pay days")