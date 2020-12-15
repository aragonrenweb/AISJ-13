# -*- coding: utf-8 -*-

from odoo import models, fields, api, _


class FormioSettings(models.TransientModel):
    """  Settings for school base module """
    _inherit = "res.config.settings"

    adm_default_application_formio_reference_form_id = fields.Many2one(
        'formio.form',
        string="Default Application Formio Reference Form",
        config_parameter='adm_formio.default_application_formio_reference_id')

    @api.model
    def get_values(self):
        res = super().get_values()
        Param = self.env['ir.config_parameter'].sudo()
        appl_reference_form_id = Param.get_param(
            'adm_formio.default_application_formio_reference_id', False)
        if appl_reference_form_id:
            res.update(
                adm_default_application_formio_reference_form_id=int(appl_reference_form_id)
                )
        return res

    def set_values(self):
        super().set_values()
        self.env['ir.config_parameter'].sudo().set_param(
            'adm_formio.default_application_formio_reference_id',
            str(self.adm_default_application_formio_reference_form_id.id))
