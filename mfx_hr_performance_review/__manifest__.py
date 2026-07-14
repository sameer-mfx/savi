{
    'name': 'HR Performance Review',
    'version': '17.0.1.0.0',
    'category': 'Human Resources',
    'summary': 'Employee Performance Reviews, Appraisals & Goal Tracking',
    'description': """
HR Performance Review Module
============================
A comprehensive performance management system for Odoo 17 Community Edition.

Features:
---------
* Review Cycles (Quarterly, Semi-Annual, Annual)
* Customizable Review Templates with weighted criteria
* Self-Assessment by employees
* Manager Evaluation
* Goal Setting & Tracking with deadlines
* Configurable Rating Scale (1-5)
* Multi-stage Workflow (Draft → Self-Review → Manager Review → HR Approved → Done)
* Performance History tracking per employee
* Department-wise Performance Dashboard
* Email notifications at each stage
* Automatic update of employee performance rating
    """,
    'author': 'Macrofix',
    'website': 'https://macrofix.com',
    'license': 'LGPL-3',
    'depends': [
        'hr',
        'mail',
    ],
    'data': [
        # Security
        'security/mfx_hr_performance_review_security.xml',
        'security/ir.model.access.csv',
        # Data
        'data/ir_sequence_data.xml',
        'data/mail_template_data.xml',
        'data/ir_cron_data.xml',
        # Wizard
        'wizard/generate_reviews_wizard_views.xml',
        # Views
        'views/review_cycle_views.xml',
        'views/review_template_views.xml',
        'views/performance_review_views.xml',
        'views/review_goal_views.xml',
        'views/hr_employee_views.xml',
        'views/user_manual_views.xml',
        'views/menu_views.xml',
    ],
    'assets': {
        'web.assets_backend': [
            'mfx_hr_performance_review/static/src/js/user_manual.js',
            'mfx_hr_performance_review/static/src/xml/user_manual_template.xml',
            'mfx_hr_performance_review/static/src/scss/user_manual.scss',
        ],
    },
    'demo': [],
    'images': ['static/description/icon.png'],
    'installable': True,
    'application': True,
    'auto_install': False,
}
