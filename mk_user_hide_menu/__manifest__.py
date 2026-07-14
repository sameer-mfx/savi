# -*- coding: utf-8 -*-
##############################################################################
#
#    OpenERP, Open Source Management Solution
#    Copyright (C) 2015 Master Key.
#
##############################################################################

{
    'name': 'User Hide Menu',
    'version': '17.0.1.0',
    'sequence': 2,
    'category': 'base',
    'description':
         """
        User Hide Menu.
         """,
    'summary': 'User Hide Menu',
    'author': 'Master Key',
    'depends': ['base'],
    'data': [
        'views/res_user_view.xml',
    ],
    'demo': [],
    'test': [],
    'css': [],
    'qweb': [],
    'js': [],
    'images': [],
    'installable': True,
    'application': True,
    'auto_install': False,
}
# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:
