# -*- coding: utf-8 -*-

from odoo import models, fields, api, _


class ImportField(models.Model):
    _name = 'import_to_facts.import_field'

    field_id = fields.Many2one('ir.model.fields', string='Odoo field')
    alias_field = fields.Char('Alias')

