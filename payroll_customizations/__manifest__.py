{
    'name': 'Savi_Vision-Macrofix Payroll Customizations',
    'author': 'Macrofix',
    'website': 'https://www.macrofix.com',
    'version': '1.4',
    'depends': ['hr_payroll_community', 'hr_payroll_account_community'],
    'data': [
        'views/payroll_views.xml',
        'views/hr_payslip_line_views.xml',
        'views/user_manual_views.xml',
    ],
    'assets': {
        'web.assets_backend': [
            'payroll_customizations/static/src/js/user_manual.js',
            'payroll_customizations/static/src/xml/user_manual_template.xml',
            'payroll_customizations/static/src/scss/user_manual.scss',
        ],
    },
    'installable': True,
    'application': True,
    'auto_install': False,
    'license': 'LGPL-3'
}