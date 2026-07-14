# -*- coding: utf-8 -*-
##############################################################################
#
#    OpenERP, Open Source Management Solution
#    Copyright (C) Macrofix (<https://macrofix.com/>).
#
##############################################################################

{
    'name': 'Service Order',
    'author': 'Macrofix',
    'website': 'https://www.macrofix.com',
    'version': '1.0',
    'depends': ['sale', 'stock', 'hr'],
    'category': 'Service Order',
    'data': [
        'data/service_order_sequence.xml',
        'data/service_access_groups.xml',
        'data/cron_create_srn.xml',
        'data/srn_email_template.xml',
        'security/ir.model.access.csv',
        'views/employee_views.xml',
        'views/service_order_views.xml',
        'views/srn_views.xml',
        'views/replaced_item_views.xml',
        'views/service_order_site_checkin_views.xml'
    ],
    'installable': True,
    'application': True,
    'auto_install': False,
    'license': 'LGPL-3'
}