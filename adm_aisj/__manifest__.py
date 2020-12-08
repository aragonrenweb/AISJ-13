# -*- coding: utf-8 -*-

{
    'name': "Admission AISJ Customization",

    'summary': """ Module for custom AISJ Admission Process """,

    'description': """ Module for custom AISJ Admission Process """,

    'author': "Eduweb Group SL",
    'website': "http://www.eduwebgroup.com",

    # Categories can be used to filter modules in modules listing
    # Check https://github.com/odoo/odoo/blob/12.0/odoo/addons/base/data/ir_module_category_data.xml
    # for the full list
    'category': 'Admission',
    'version': '1',

    # any module necessary for this one to work correctly
    'depends': ['adm'],

    # always loaded
    'data': [
        'views/views_application.xml'
        ],
    # 'qweb': [ ],
    # 'application': True
    }


