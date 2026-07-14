# -*- coding: utf-8 -*-
##############################################################################
#
#    OpenERP, Open Source Management Solution
#    Copyright (C) Macrofix (<https://macrofix.com/>).
#
##############################################################################

{
    "name": "Helpdesk - AMC - Service Order",
    "summary": "Add the option to create service orders from helpdesk tickets based on AMC orders.",
    "version": "17.0.1.0.0",
    "license": "LGPL-3",
    "category": "Service Order",
    "author": "Macrofix",
    "website": "https://www.macrofix.com",
    "depends": ["helpdesk_mgmt", "service_order_mfx", "amc_mfx"],
    "data": [
        "views/helpdesk_ticket_views.xml",
        # "views/service_order_views.xml",
    ]
}