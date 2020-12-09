# -*- coding: utf-8 -*-

from odoo import models, fields, api, _


class StatusHistory(models.Model):
    """ History is first in its _name to make things like
        history.foo history.boo"""
    _name = 'adm.application.history.status'

    application_id = fields.Many2one('adm.application')
    timestamp = fields.Datetime()
    note = fields.Char()
