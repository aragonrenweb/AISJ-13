# -*- coding: utf-8 -*-

from odoo import models, fields, api


class AdmApplication(models.Model):
    _inherit = "adm.application"

    def default_formio_reference_form_id(self):
        default_reference_form_id = (
            self.env['ir.config_parameter']
            .sudo().get_param(
                'adm_formio.default_application_formio_reference_id', False)
                )

        formio_form_id = self.env['formio.form']
        if default_reference_form_id:
            formio_form_id = formio_form_id.browse(
                int(default_reference_form_id)
                )
        return formio_form_id

    formio_sent_to_email = fields.Char(string="Formio sent to email")
    formio_reference_form_id = fields.Many2one(
        "formio.form",
        default=default_formio_reference_form_id)
