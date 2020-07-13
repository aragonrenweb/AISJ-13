# -*- coding: utf-8 -*-
{
    'name': "wallet",

    'summary': """
        Short (1 phrase/line) summary of the module's purpose, used as
        subtitle on modules listing or apps.openerp.com""",

    'description': """
        Long description of module's purpose
    """,

    'author': "My Company",
    'website': "http://www.yourcompany.com",

    # Categories can be used to filter modules in modules listing
    # Check https://github.com/odoo/odoo/blob/13.0/odoo/addons/base/data/ir_module_category_data.xml
    # for the full list
    'category': 'Uncategorized',
    'version': '0.1',

    # any module necessary for this one to work correctly
    'depends': [
        'base', 
        "account",
        "account_accountant",
        "product"],

    # always loaded
    'data': [
        'security/ir.model.access.csv',
        'wizard/load_wallet.xml',
        'wizard/pay_with_wallet.xml',

        'views/partner_views.xml',
        'views/wallet_views.xml',
        'views/config_views.xml',
        'views/templates.xml',

        # Inherit views
        'views/inherited/account_payment_views.xml',
        'views/inherited/account_move.xml',

        'data/add_assets.xml',
        'data/category_all_wallet.xml',
        'data/menu.xml',
    ],
}
