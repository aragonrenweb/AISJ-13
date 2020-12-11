#-*- coding:utf-8 -*-

from odoo import models, fields, api


class AdmApplication(models.Model):
    _inherit = "adm.application"

    formio_sent_to_email = fields.Char(string="Formio sent to email")
    formio_reference_form_id = fields.Many2one("formio.form")
