# -*- coding: utf-8 -*-
##############################################################################
#
#    OpenERP, Open Source Management Solution
#    Copyright (C) Macrofix (<https://macrofix.com/>).
#    Author: Sameer.
#
##############################################################################

{
    'name': 'MFX Project AMC Conversion',
    'author': 'Macrofix',
    'website': 'https://www.macrofix.com',
    'version': '1.0',
    'depends': ['mfx_projects_management', 'amc_mfx'],
    'category': 'Project Management',
    'data': [
        'security/ir.model.access.csv',
        'views/project_stage_views.xml',
        'views/project_views.xml',
        'wizard/project_amc_wizard_views.xml'
    ],
    'installable': True,
    'application': True,
    'auto_install': False,
    'license': 'OPL-1'
}