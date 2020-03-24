# -*- coding: utf-8 -*-
from odoo import http


class NewAccountMove2(http.Controller):
    @http.route('/new_account_move_2/new_account_move_2/', auth='public')
    def index(self, **kw):
         return "Hello, world"
        
    def list(self, **kw):
         return http.request.render('new_account_move_2.listing', {
             'root': '/new_account_move_2/new_account_move_2',
             'objects': http.request.env['new_account_move_2.new_account_move_2'].search([]),
         })

    @http.route('/new_account_move_2/new_account_move_2/objects/<model("new_account_move_2.new_account_move_2"):obj>/', auth='public')
    def object(self, obj, **kw):
         return http.request.render('new_account_move_2.object', {
             'object': obj
         })
