
from odoo import fields, models, api
import logging

_logger = logging.getLogger(__name__)


class LoadWallet(models.TransientModel):
    _name = 'load.wallet'
    _description = 'Load wallet...'

    def _get_company_currency(self):
        for record in self:
            record.currency_id = self.env.company.currency_id

    currency_id = fields.Many2one('res.currency', compute='_get_company_currency', readonly=True,
                                  string="Currency", help='Utility field to express amount currency')

    amount = fields.Monetary("Amount")
    payment_ids = fields.Many2many("account.payment")
    wallet_category_id = fields.Many2one("wallet.category", "Wallet Category")
    wallet_journal_category_id = fields.Many2one(related="wallet_category_id.journal_category_id")

    @api.depends('amount', 'payment_ids')
    def _onchange_amount(self):
        for record in self:

            max_amount = 0.0

            if payment_ids:
                max_amount = sum(record.payment_ids.mapped(lambda payment: payment.amount))

            if record.amount > max_amount:
                record.amount = max_amount

    def load_wallet(self):
        self.ensure_one()
        context = self.env.context
        partner_ids = context.get("active_ids", False)

        if partner_ids:
            resPartner = self.env["res.partner"]
            resPartner.browse(partner_ids).load_wallet(self.payment_ids.ids, self.wallet_category_id.ids, self.amount)
