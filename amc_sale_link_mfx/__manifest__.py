# -*- coding: utf-8 -*-
##############################################################################
#
#    OpenERP, Open Source Management Solution
#    Copyright (C) Macrofix (<https://macrofix.com/>).
#
##############################################################################

{
    'name': 'AMC Sale Link',
    'version': '17.0.1.0.0',
    'depends': ['amc_mfx', 'sale', 'custom_crm_mfx'],
    'data': [
        'views/amc_order_views.xml',
        'views/sale_order_views.xml',
    ],
    'installable': True,
    'application': True,
}