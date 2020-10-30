# -*- coding: utf-8 -*-

{
    'name': "Admission Reporting",

    'summary': """
        Reporting Module
    """,

    'description': """""",

    'author': "Eduweb Group SL",
    'website': "http://www.yourcompany.com",

    # Categories can be used to filter modules in modules listing
    # Check https://github.com/odoo/odoo/blob/12.0/odoo/addons/base/data/ir_module_category_data.xml
    # for the full list
    'category': 'Admission',
    'version': '0.1',

    # any module necessary for this one to work correctly
    'depends': ['base', 'adm', 'web_dashboard', 'web_cohort', 'web_map'],

    # always loaded
    'data': [
        'views/adm_reporting_inquiry_dashboard.xml',
        'views/adm_reporting_application_dashboard.xml',
        'views/adm_reporting_menus.xml',
    ],
    'application': True
}

