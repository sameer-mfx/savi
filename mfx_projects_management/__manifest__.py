# -*- coding: utf-8 -*-
##############################################################################
#
#    OpenERP, Open Source Management Solution
#    Copyright (C) Macrofix (<https://macrofix.com/>).
#    Author: Sameer.
#
##############################################################################

{
    'name': 'MFX Project Management',
    'author': 'Macrofix',
    'website': 'https://www.macrofix.com',
    'version': '1.0',
    'depends': ['project', 'sale', 'sale_project', 'stock'],
    'category': 'Project Management',
    'data': [
        'security/ir.model.access.csv',
        'views/project_task_stage_views.xml',
        'views/project_task_views.xml',
        'views/project_views.xml',
    ],
    'external_dependencies': {
        'python': ['xlsxwriter']
    },
    'installable': True,
    'application': True,
    'auto_install': False,
    'license': 'OPL-1'
}