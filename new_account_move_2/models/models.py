# -*- coding: utf-8 -*-

from odoo import models, fields, api


class new_account_move_2(models.Model): 
    _description = 'new_account_move_2.new_account_move_2'
    _inherit = 'account.move'

    name = fields.Char()
    value = fields.Integer()
    value2 = fields.Float(compute="_value_pc", store=True)
    description = fields.Text()

    @api.depends('value')
    def _value_pc(self):
        for record in self:
            record.value2 = float(record.value) / 100
            
    #def calculate_amount(self):
        #super()._compute_balance(self)
