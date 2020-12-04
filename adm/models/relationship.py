'''
Created on Feb 1, 2020

@author: LuisMora
'''
from odoo import models, fields, _


class Relationship(models.Model):
    _name = "adm.relationship"

    partner_1 = fields.Many2one("res.partner", string="Partner 1", required=True, ondelete="cascade")
    partner_2 = fields.Many2one("res.partner", string="Partner", required=True, ondelete="cascade")

    relationship_type = fields.Selection(
        [('sibling', "Sibling"), ('father', "Father"), ('mother', "Mother"), ('uncle', "Uncle"), ('grandmother', "Grandmother"), ('grandfather', "Grandfather"),
            ('other', "Other"), ], string="Type", default='other')

    custodial_rights = fields.Selection([('yes', _('Yes')), ('no', _('No')), ], string="Custiodial rights", default="no")

    is_emergency_contact = fields.Boolean("Is an emergency contact?")
