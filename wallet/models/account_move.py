# -*- coding: utf-8 -*-

from odoo import fields, models, api


class AccountMove (models.Model):
    _inherit = 'account.move'

    def pay_with_wallet(self, wallet_payment_dict):

        if wallet_payment_dict:

            accountMoveEnv = self.env["account.move"]
            for move_id in self:
                invoice_line_ids = []

                journal_ids = set(map(lambda wallet_id: wallet_id.journal_category_id, wallet_payment_dict.keys()))

                for journal_id in journal_ids:
                    filtered_wallet_line_ids = {wallet_id: amount
                                                for wallet_id, amount in wallet_payment_dict.items()
                                                if wallet_id.journal_category_id == journal_id}

                    if filtered_wallet_line_ids:
                        for wallet_id, amount in filtered_wallet_line_ids.items():
                            invoice_line_ids.append((0, 0, {
                                    "product_id": wallet_id.product_id.id,
                                    "price_unit": amount,
                                    "quantity": 1,
                                })
                            )

                        credit_note_id = accountMoveEnv.create({
                            "type": "out_refund",
                            "partner_id": move_id.partner_id,
                            "journal_id": journal_id.id,
                            "invoice_line_ids": invoice_line_ids,
                        })

                        receivable_line_id = credit_note_id.line_ids.\
                            filtered(lambda move_line_id: move_line_id.account_id.user_type_id.type == 'receivable')

                        credit_note_id.post()
                        move_id.js_assign_outstanding_line(receivable_line_id.id)
