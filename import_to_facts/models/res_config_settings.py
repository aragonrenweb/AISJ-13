# -*- coding: utf-8 -*-

from odoo import models, fields, api, _


class AdmissionsSettings(models.TransientModel):
    """  Settings for school base module """
    _inherit = "res.config.settings"

    adm_application_json_field_ids = fields.Many2many(
        'import_to_facts.import_field',
        string="Application required fields",
        store=True,
        relation='import_to_facts_json_fields')

    @api.model
    def get_values(self):
        res = super(AdmissionsSettings, self).get_values()

        config_parameter = self.env['ir.config_parameter'].sudo()
        adm_application_json_field_str = config_parameter.get_param(
            'adm_application_json_field_ids', '')
        application_json_fields = [
            int(e) for e in adm_application_json_field_str.split(',')
            if e.isdigit()
        ]

        res.update({
            'adm_application_json_field_ids': application_json_fields
        })

        return res

    def set_values(self):
        for settings in self:
            config_parameter = self.env['ir.config_parameter'].sudo()
            config_parameter.set_param(
                'adm_application_json_field_ids', ",".join(
                    map(str, settings.adm_application_json_field_ids.ids)))