# -*- coding: utf-8 -*-
##############################################################################
#
#    OpenERP, Open Source Management Solution
#    Copyright (C) Macrofix (<https://macrofix.com/>).
#    Author: Sameer.
#
##############################################################################

{
    'name': 'Savi_Vision-Macrofix Customizations',
    'author': 'Macrofix',
    'website': 'https://www.macrofix.com',
    'version': '1.3.1',
    'depends': ['crm', 'general_template', 'sale', 'sale_management', 'sale_margin', 'product', 'purchase'],
    'data': [
        'security/ir.model.access.csv',
        'data/employee_attendance_automated.xml',
        'data/send_anniversary_mails.xml',
        'data/accounting_access_groups.xml',
        'data/sale_reminders.xml',
        'data/purchase_cancel_email_template.xml',
        'views/crm_lead_views.xml',
        'views/product_supplier_info_menu.xml',
        'views/employee_views.xml',
        # 'views/task_line_views.xml',
        'views/sale_order_views.xml',
        'views/sale_purchase_custom_templates.xml',
        'views/report_sale_force_quotation.xml',
        'views/sale_quotation_any_state_template.xml',
        'views/company_views.xml',
        'views/purchase_order_line_views.xml',
        'views/sale_reminder_template.xml',
        'views/accounting_buttons_visibility_views.xml',
        'views/product_template_views.xml',
        'views/partner_views.xml',
        'views/purchase_cancel_report.xml'
    ],
    'installable': True,
    'application': True,
    'auto_install': False,
    'license': 'LGPL-3'
}