# -*- coding: utf-8 -*-
##############################################################################
#
#    OpenERP, Open Source Management Solution
#    Copyright (C) Macrofix (<https://macrofix.com/>).
#
##############################################################################

{
    'name': 'Service Order - Sales',
    'author': 'Macrofix',
    'website': 'https://www.macrofix.com',
    'version': '1.0',
    'depends': ['sale', 'service_order_mfx'],
    'category': 'Service Order',
    'data': [
        'security/ir.model.access.csv',
        'wizard/create_service_wizard_views.xml',
        'views/sale_order_views.xml',
        'views/service_order_views.xml',
    ],
    'installable': True,
    'application': True,
    'auto_install': False,
    'license': 'LGPL-3'
}