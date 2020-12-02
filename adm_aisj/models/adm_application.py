# -*- coding: utf-8 -*-

from odoo import models, fields, api, _


class AdmApplication(models.Model):
    _inherit = 'adm.application'

    passport_number_1 = fields.Char()
    passport_number_2 = fields.Char()
    passport_expiration_date = fields.Date()
    expected_starting_date = fields.Date()
