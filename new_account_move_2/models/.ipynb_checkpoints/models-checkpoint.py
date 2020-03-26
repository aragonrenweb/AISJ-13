# -*- coding: utf-8 -*-

from odoo import models, fields, api


class new_account_move_2(models.Model): 
    _inherit = 'account.move'

    def calculateAmount(self):
        super()._onchange_invoice_date()
        super()._recompute_dynamic_lines()