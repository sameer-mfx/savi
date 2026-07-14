{
    "name": "Merge Duplicate Products",
    "summary": "Merge duplicate products at once into a single product which you require as main product",
    "version": "17.0.1.0.0",
    "license": "LGPL-3",
    "category": "Sales/Sales",
    "depends": ["product"],
    "data": [
        "security/res_groups.xml",
        "security/ir.model.access.csv",
        "wizard/base_product_merge_view.xml",
    ],
    "installable": True,
    "external_dependencies": {
        "python": ["openupgradelib"],
    }
}