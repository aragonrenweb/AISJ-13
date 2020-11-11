# -*- coding: utf-8 -*-
{
    'name': 'AISJ Access Rights',

    'summary': """ AISJ Access Rights """,

    'description': """
        AISJ Access Rights
    """,

    'author': 'Eduwebgroup',
    'website': 'http://www.eduwebgroup.com',

    'category': 'Extra Tools',
    'version': '1.0',

    'depends': [
        'account',
        'purchase',
        'hide_menu_by_group',
    ],

    'data': [
        'data/res_groups_data.xml',
        'security/ir.model.access.csv',
        'security/account_move_security.xml',
        'views/account_move_views.xml',
    ],
}