# -*- coding: utf-8 -*-

from odoo import fields, models, api


class AccountMove (models.Model):
    _inherit = 'account.move'

    def pay_with_wallet(self, wallet_payment_line_ids):
        if type(wallet_payment_line_ids) == list:
            wallet_payment_line_ids = self.env["wallet.payment.line"].browse(wallet_payment_line_ids)
        elif type(wallet_payment_line_ids) == int:
            wallet_payment_line_ids = self.env["wallet.payment.line"].browse([wallet_payment_line_ids])

        accountMoveEnv = self.env["account.move"]

        for move_id in self:

            invoice_line_ids = []

            journal_ids = wallet_payment_line_ids.mapped("wallet_id").mapped("journal_category_id")

            for journal_id in journal_ids:
                filtered_wallet_line_ids = wallet_payment_line_ids.\
                    filtered(lambda line_id: line_id.wallet_id.journal_category_id == journal_id)

                if filtered_wallet_line_ids:
                    for wallet_line_id in filtered_wallet_line_ids:
                        invoice_line_ids.append((0, 0, {
                                "product_id": wallet_line_id.wallet_id.product_id.id,
                                "price_unit": wallet_line_id.amount,
                                "quantity": 1,
                            })
                        )

                    move_id = accountMoveEnv.create({
                        "type": "out_refund",
                        "partner_id": move_id.partner_id,
                        "journal_id": journal_id.id,
                        "invoice_line_ids": invoice_line_ids,
                    })

                    move_id.post()
                    receivable_line_id = move_id.line_ids.\
                        filtered(lambda move_line_id: move_line_id.account_id.user_type_id.type == 'receivable')

                    move_id.js_assign_outstanding_line(receivable_line_id.id)
