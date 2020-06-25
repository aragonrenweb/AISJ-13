from odoo import fields, models, api


class ProductProduct (models.Model):
    _inherit = 'product.product'

    facts_id = fields.Char("Fact id", related="categ_id.facts_id")

class ProductTemplate (models.Model):
    _inherit = 'product.template'

    facts_id = fields.Char("Fact id", related="categ_id.facts_id")
