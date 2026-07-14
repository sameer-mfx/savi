# -*- coding: utf-8 -*-
##############################################################################
#
#    OpenERP, Open Source Management Solution
#    Copyright (C) Macrofix (<https://macrofix.com/>).
#
##############################################################################

{
    "name": "Helpdesk Service Order",
    "summary": "Add the option to link between service orders and helpdesk tickets.",
    "version": "17.0.0.0.0",
    "license": "LGPL-3",
    "category": "Service Order",
    "author": "Macrofix",
    "website": "https://www.macrofix.com",
    "depends": ["helpdesk_mgmt", "service_order_mfx"],
    "data": [
        "views/helpdesk_ticket_views.xml",
        "views/service_order_views.xml",
    ],
    "development_status": "Production/Stable",
    "auto_install": True,
}