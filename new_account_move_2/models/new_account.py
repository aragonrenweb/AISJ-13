from odoo import models, fields, api

class new_account(models.Model):
    _inherit='acount.move'
    
    def calculate_amount(self):
        super()._compute_balance(self)