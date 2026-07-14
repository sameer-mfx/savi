# -*- coding: utf-8 -*-
# Part of AppJetty. See LICENSE file for full copyright and licensing details.

{
    'name': 'Clever All In One Report Templates',
    'author': 'AppJetty',
    'license': 'OPL-1',
    'version': '17.0',
    'category': 'Accounting',
    'depends': [
        'account',
        'sale_management',
        'delivery',
        'stock',
        'purchase',
        'partner_autocomplete',
        'stock_delivery',
    ],
    'website': 'https://www.appjetty.com',
    'support': 'support@appjetty.com',
    'description': '''Get Diverse Templates For PO/RFQ/SO/Delivery Note/Picking List In One Go!
Professional templates , Professional Report Templates, Sales Order Report Template, Quotation Report Template,
Purchase order Report Template, Purchase Requestion Template, Credit Memo Report Template, Picking List report Template,
SO report template, Po Report Template
''',
    'summary': 'Get Diverse Templates For PO/RFQ/SO/Delivery Note/Picking List One Go!',
    'data': [
        'data/template_data.xml',
        'security/base_security.xml',
        'security/ir.model.access.csv',
        'views/report_extra_content_view.xml',
        'views/templates.xml',
        'views/sale_templates.xml',
        'views/purchase_templates.xml',
        'views/picking_templates.xml',
        'views/invoice_templates.xml',
        'views/quotation_templates.xml',

        'views/template_report.xml',
        'views/res_company_view.xml',
        'views/res_partner_view.xml',
        'views/sale_view.xml',
        'views/stock_view.xml',
        'views/purchase_view.xml',
        'views/invoice_view.xml',
        'views/preview_template.xml',

        'views/polished_sale.xml',
        'views/morden_sale.xml',
        'views/vintage_sale.xml',
        'views/bold_sale.xml',
        'views/corporate_sale.xml',
        'views/classic_sale.xml',

        'views/polished_delivery.xml',
        'views/morden_delivery.xml',
        'views/bold_delivery.xml',
        'views/corporate_delivery.xml',
        'views/vintage_delivery.xml',
        'views/classic_delivery.xml',

        'views/polished_picking.xml',
        # 'views/morden_picking.xml',
        'views/vintage_picking.xml',
        'views/bold_picking.xml',
        'views/corporate_picking.xml',
        'views/classic_picking.xml',

        'views/vintage_purchase.xml',
        'views/bold_purchase.xml',
        'views/corporate_purchase.xml',
        'views/polished_purchase.xml',
        'views/morden_purchase.xml',
        'views/classic_purchase.xml',

        'views/polished_quotation.xml',
        'views/vintage_quotation.xml',
        'views/bold_quotation.xml',
        'views/corporate_quotation.xml',
        'views/morden_quotation.xml',
        'views/classic_quotation.xml',

        'views/morden_invoice.xml',
        'views/bold_invoice.xml',
        'views/corporate_invoice.xml',
        'views/polished_invoice.xml',
        'views/custom_receipts.xml',
        # 'views/vintage_invoice.xml',
        'views/classic_invoice.xml',
    ],
    'assets': {
        'web.report_assets_common': [
            'general_template/static/src/css/template.css',
        ],
    },
    'external_dependencies': {
        'python': ['img2pdf', 'fpdf', 'num2words']
    },
    'images': ['static/description/splash-screen.png'],
    'installable': True,
    'auto_install': False,
    'web_preload': True,
}
