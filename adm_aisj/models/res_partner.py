# -*- coding: utf-8 -*-

from odoo import models, fields, api, _


class ResPartner(models.Model):
    _inherit = 'res.partner'

    c_aisj_employer = fields.Char()
    c_aisj_occupation = fields.Char()

