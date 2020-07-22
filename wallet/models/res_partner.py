# -*- coding: utf-8 -*-

import logging
from odoo import fields, models, api

logger = logging.getLogger(__name__)


class ResPartner (models.Model):
    _inherit = 'res.partner'

    def execute_autoclear(self):
        self.autoclear_payments()
        self.autoclear_moves()

    def autoclear_moves(self):
        # Yes, I KNOW THAT I CAN USE INVOICE_IDS! But, in the future, we are going to make
        # the domain more complex and even with invoices that haven't their partner as customer
        for partner_id in self:
            move_ids = self.env["account.move"].search(
                [
                    ("partner_id", "=", partner_id.id),
                    ("invoice_payment_state", "!=", "paid"),
                    ("state", "=", "posted"),
                    ("type", "=", "out_invoice"),
                ]
            )
            move_ids_wallet_amounts = move_ids.get_available_wallet_amounts()
            if move_ids_wallet_amounts:
                partner_wallet_amounts = move_ids_wallet_amounts[partner_id]
                move_ids.pay_with_wallet(partner_wallet_amounts)

    def autoclear_payments(self):
        """ This will load payment to wallet automatically """
        for record in self:
            wallet_ids = self.env["wallet.category"].search([])
            payment_grouped = {}
            default_wallet_id = self.env.ref("wallet.default_wallet_category")
            
            # We find and group payment with wallets
            for wallet_id in wallet_ids:
                domain_payment_wallet_id = wallet_id.id
                if wallet_id == default_wallet_id:
                    domain_payment_wallet_id = False
                payment_ids = self.env["account.payment"].search(
                    [
                        ("partner_id", "=", self.id), 
                        ("unpaid_amount", ">", 0), 
                        ("wallet_id", "=", domain_payment_wallet_id),
                        ("state", "in", ["posted", "sent", "reconciled"]),
                    ]
                )
                if payment_ids:
                    payment_grouped[wallet_id] = payment_ids
            
            # We start load wallet to partners
            for wallet_id, payment_ids in payment_grouped.items():
                amount = sum(payment_ids.mapped("unpaid_amount"))
                record.load_wallet(payment_ids, wallet_id, amount)
                logger.info("Wallet loaded to %s with: wallet_id: %s, payment_ids: %s, amount: %s" % (record,
                                                                                                      wallet_id,
                                                                                                      payment_ids,
                                                                                                      amount))

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
