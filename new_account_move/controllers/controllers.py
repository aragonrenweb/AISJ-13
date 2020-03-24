# -*- coding: utf-8 -*-
from odoo import http


 class NewAccountMove(http.Controller):
     @http.route('/new_account_move/new_account_move/', auth='public')
     def index(self, **kw):
         return "Hello, world"

     @http.route('/new_account_move/new_account_move/objects/', auth='public')
     def list(self, **kw):
         return http.request.render('new_account_move.listing', {
             'root': '/new_account_move/new_account_move',
             'objects': http.request.env['new_account_move.new_account_move'].search([]),
         })

     @http.route('/new_account_move/new_account_move/objects/<model("new_account_move.new_account_move"):obj>/', auth='public')
     def object(self, obj, **kw):
         return http.request.render('new_account_move.object', {
             'object': obj
         })
