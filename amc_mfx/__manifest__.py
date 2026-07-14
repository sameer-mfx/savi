# -*- coding: utf-8 -*-
##############################################################################
#
#    OpenERP, Open Source Management Solution
#    Copyright (C) Macrofix (<https://macrofix.com/>).
#    Author: Sameer.
#
##############################################################################

{
    'name': 'AMC',
    'author': 'Macrofix',
    'website': 'https://www.macrofix.com',
    'version': '1.0',
    'depends': ['stock'],
    'category': 'AMC',
    'data': [
        'data/amc_sequence.xml',
        'data/amc_access_groups.xml',
        'security/ir.model.access.csv',
        'report/amc_order_report.xml',
        'data/amc_email_template.xml',
        'data/cron_update_amc_validity.xml',
        'views/amc_order_views.xml',
        'views/amc_services_views.xml',
        'views/amc_visit_views.xml',
        'views/amc_lot_details_views.xml',
        'views/amc_replacement_views.xml',
        'wizard/amc_visit_wizard_views.xml'
    ],
    'installable': True,
    'application': True,
    'auto_install': False,
    'license': 'OPL-1'
}