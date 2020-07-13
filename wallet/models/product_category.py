# -*- coding: utf-8 -*-

import logging

from odoo import _, api, fields, models

_logger = logging.getLogger(__name__)


class ProductCategory(models.Model):
    _inherit = "product.category"

    wallet_ok = fields.Boolean("For wallet use")

    def get_parent_count(self):
        self.ensure_one()
        if self.parent_id:
            return 1 + get_parent_account(self.parent_id)
        else:
            return 1
