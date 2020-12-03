# -*- coding: utf-8 -*-

from odoo import models, fields, api, _


class AdmApplication(models.Model):
    _inherit = 'adm.application'

    passport_number_1 = fields.Char()
    passport_number_2 = fields.Char()
    passport_expiration_date = fields.Date()
    expected_starting_date = fields.Date()

    # Parent/Guardian relation
    # I know we can use relationship_ids field, but, this can make the things really
    # complicated.
    # So, a simple silution is create a specific field for then
    guardian_relationship1_id = fields.Many2one('adm.relationship')
    guardian_relationship2_id = fields.Many2one('adm.relationship')

    guardian1_partner_id = fields.Many2one('res.partner')
    guardian2_partner_id = fields.Many2one('res.partner')
