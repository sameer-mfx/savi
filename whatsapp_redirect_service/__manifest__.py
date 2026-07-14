{
    'name': 'Send Whatsapp Message from Odoo SRN',
    'author': 'Macrofix',
    'category': 'Whatsapp',
    'description': 'This module helps you to directly send messages to your contacts through WhatsApp web.',
    'website': 'https://www.macrofix.com',
    'version': '1.3.1',
    'depends': ['service_order_mfx', 'whatsapp_redirect'],
    'data': [
        'data/whatsapp_template.xml',
        'views/srn_views.xml',
    ],
    'installable': True,
    'application': True,
    'auto_install': False,
    'license': 'LGPL-3'
}