# -*- coding: utf-8 -*-

from odoo import models, fields, api

class new_account_move_2(models.Model): 
    _inherit = 'account.move'

    def calculateAmount(self):
        super()._onchange_invoice_date()
        
    def calculateMoveLineAmount(self):
        super()._compute_amount()
    
    def recomputeLines(self):
        super()._recompute_dynamic_lines(recompute_all_taxes=True, recompute_tax_base_amount=True)