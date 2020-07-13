# -*- coding: utf-8 -*-
# from odoo import http


# class Wallet(http.Controller):
#     @http.route('/wallet/wallet/', auth='public')
#     def index(self, **kw):
#         return "Hello, world"

#     @http.route('/wallet/wallet/objects/', auth='public')
#     def list(self, **kw):
#         return http.request.render('wallet.listing', {
#             'root': '/wallet/wallet',
#             'objects': http.request.env['wallet.wallet'].search([]),
#         })

#     @http.route('/wallet/wallet/objects/<model("wallet.wallet"):obj>/', auth='public')
#     def object(self, obj, **kw):
#         return http.request.render('wallet.object', {
#             'object': obj
#         })
