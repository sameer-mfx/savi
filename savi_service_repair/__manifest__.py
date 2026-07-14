{
    "name": "SAVI Service Repair",
    "summary": "Repair case workflow for service and product repair operations",
    "version": "17.0.1.0.0",
    "category": "Services",
    "author": "Macrofix",
    "website": "https://www.macrofix.com",
    "depends": [
        "service_order_mfx",
        "helpdesk_mgmt",
        "stock",
        "account",
    ],
    "data": [
        "security/ir.model.access.csv",
        "data/repair_sequence.xml",
        "views/service_repair_views.xml",
        "views/service_order_views.xml",
    ],
    "installable": True,
    "application": False,
    "auto_install": False,
    "license": "LGPL-3",
}
