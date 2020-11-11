#-*- coding:utf-8 -*-

from odoo import models, fields, api

class AdmApplication(models.Model):
    _inherit = "adm.application"

    teacher_assessment_email = fields.Char(string="Teacher Assessment Email")
    teacher_assessment_form_id = fields.Many2one(string="Teacher Assessment Form",
        comodel_name="formio.form")