# -*- coding: utf-8 -*-

from odoo import fields, models, api


class ResPartner (models.Model):
    _inherit = 'res.partner'

    def load_wallet(self, payment_ids, wallet_id, amount):
        if type(payment_ids) == list:
            payment_ids = self.env["account.payment"].browse(payment_ids)

        if type(wallet_id) == list:
            wallet_id = self.env["wallet.category"].browse(wallet_id)
        elif type(wallet_id) == int:
            wallet_id = self.env["wallet.category"].browse([wallet_id])

        accountMoveEnv = self.env["account.move"]

        move_ids = self.env["account.move"]

        for record in self:
            move_id = accountMoveEnv.create({
                "type": "out_invoice",
                "partner_id": record.id,
                "journal_id": wallet_id.journal_category_id.id,
                "invoice_line_ids": [(0, 0, {
                    "product_id": wallet_id.product_id.id,
                    "price_unit": amount,
                    "quantity": 1,
                })],
            })

            move_id.post()

            payments_receivable_line_ids = payment_ids.move_line_ids.filtered(lambda move_line_id: move_line_id.account_id.user_type_id.type == 'receivable')

            for receivable_line_id in payments_receivable_line_ids:
                move_id.js_assign_outstanding_line(receivable_line_id.id)

            move_ids += move_id

        return move_ids
