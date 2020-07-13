from odoo import fields, models, api
import logging

_logger = logging.getLogger(__name__)


class PayWithWallet(models.TransientModel):
    _name = 'pay.with.wallet'
    _description = 'Pay with wallet...'

    @api.depends("partner_id")
    def _compute_wallet_ids(self):
        self.ensure_one()
        context = self._context
        active_move_ids = context.get("active_id", False)

        if active_move_ids:
            walletCategoryEnv = self.env["wallet.category"]
            available_wallets = walletCategoryEnv
            move_ids = self.env["account.move"].browse(active_move_ids)
            for move_id in move_ids:
                partner_id = move_id.partner_id
                wallet_ids = walletCategoryEnv.search([])

                for wallet_id in wallet_ids:
                    amount_total = walletCategoryEnv.get_wallet_amount(partner_id, wallet_id)

                    if amount_total > -abs(wallet_id.credit_limit):
                        available_wallets += wallet_id

            # family_ids = self.partner_id.family_ids.ids
            self.wallet_ids = available_wallets

    def pay_with_wallet(self):
        self.ensure_one()

        context = self._context
        active_move_ids = context.get("active_ids", False)

        if active_move_id:
            move_ids = self.env["account.move"].browse(active_move_ids)
            for move_id in move_ids:
                move_id.pay_with_wallet(self.wallet_payment_line_ids)

    def _get_default_lines(self):

        context = self._context
        active_move_ids = context.get("active_ids", False)

        walletCategoryEnv = self.env["wallet.category"]

        if active_move_ids:
            move_ids = self.env["account.move"].browse(active_move_ids)
            partner_id = move_ids.mapped("partner_id")
            partner_id.ensure_one()

            move_line_ids = move_ids.mapped("invoice_line_ids")
            category_ids = move_line_ids.mapped("product_id").mapped("categ_id")

            # We are going to use this dict to get the total to pay for every wallet
            # if the wallet is full we stop add from adding
            wallet_dict = {}
            walletCategoryEnv.search([]).mapped(
                lambda wallet: wallet_dict.update({wallet.id: wallet.get_wallet_amount(partner_id, wallet)}))
            for category_id in category_ids:
                same_category_amount = sum(move_line_ids.
                                           filtered(lambda line_id: line_id.product_id.categ_id == category_id).
                                           mapped("price_total"))
                wallet_id = walletCategoryEnv.find_next_available_wallet(partner_id, category_id)
                partner_wallet_amount = walletCategoryEnv.get_wallet_amount(partner_id, wallet_id)

                # if


    partner_id = fields.Many2one("res.partner", required=True)
    wallet_ids = fields.Many2many("wallet.category", compute="_compute_wallet_ids")
    wallet_payment_line_ids = fields.Many2many("wallet.payment.line", string="Wallets", default=_get_default_lines)


class WalletPaymentLine(models.TransientModel):
    _name = "wallet.payment.line"

    wallet_id = fields.Many2one("wallet.category")
    amount = fields.Float()


    # max_amount = fields.Float()
