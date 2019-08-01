# -*- coding: utf-8 -*-

from odoo import api, models


class AccountInvoice_Report(models.Model):
    _inherit = 'account.invoice'
    _description = "Inherited invoice to print pay later details on report"

    @api.multi
    def _get_payment_modes(self):
        """ POS Invoice Report should print Payment Modes

        Fetch Payment Modes from  POS Order

        Returns
             statement_ids.
        """
        ids = []
        self.ensure_one()
        pos_order = self.env['pos.order'].sudo().search(
                            [('invoice_id', '=', self.id)])
        if pos_order:
            statement_ids = pos_order.statement_ids
            if statement_ids:
                for stmt in statement_ids:
                    ids.append({'journal': stmt.journal_id,
                                'amount': stmt.amount,
                                'create_date': stmt.create_date,
                                })
            account_payment = self.env['account.payment'].sudo().search(
                                       [('invoice_ids', 'in', self.id)])
            if account_payment:
                for pmt in account_payment:
                    ids.append({'journal': pmt.journal_id,
                                'amount': pmt.amount,
                                'create_date': pmt.create_date,
                                })
        else:
            amount = 0
            # update mode for refund invoice
            if self.payment_ids:
                for payment_id in self.payment_ids:
                    ids.append({'journal': payment_id.journal_id,
                                'amount': payment_id.amount,
                                'create_date': payment_id.create_date,
                                })

            elif self.payment_move_line_ids:
                for account_move_line in self.payment_move_line_ids:
                    if len(account_move_line.matched_debit_ids) > 1:
                        for x in account_move_line.matched_debit_ids:
                            for y in x.debit_move_id:
                                if y.invoice_id.id == self.id:
                                    amount = amount+y.debit_cash_basis
                    else:
                        amount = account_move_line.matched_debit_ids.amount
                    ids.append({'journal': account_move_line.journal_id,
                                'amount': amount,
                                'create_date': account_move_line.create_date,
                                })
        return ids

    @api.multi
    def _get_current_pending_invoice(self):
        """
            Check invoice from current session
            return : true , if POs Order
        """
        self.ensure_one()
        paid_amount = 0
        current_invoice = self.env['account.invoice'].search(
                             [('is_pending_invoice', '=', True),
                              ('id', '=', self.id)])
        if not current_invoice:
            current_invoice = self.env['account.invoice'].search(
                             [('id', '=', self.id)])
        order = self.env['pos.order'].search([
            ('invoice_id', '=', current_invoice.id)])
        if order:
            paid_amount1 = 0
            paid_amount2 = 0
            if order.statement_ids:
                paid_amount1 = sum([x.amount for x in order.statement_ids if not x.journal_id.is_pay_later])
            account_payment = self.env['account.payment'].sudo().search([
                                    ('invoice_ids', 'in', current_invoice.id)])
            if account_payment:
                paid_amount2 = sum([x.amount for x in account_payment if not x.journal_id.is_pay_later])
            paid_amount = paid_amount1 + paid_amount2
        else:
            for x in current_invoice.payment_move_line_ids:
                if len(x.matched_debit_ids) > 1:
                    for y in x.matched_debit_ids:
                        for z in y.debit_move_id:
                            if z.invoice_id.id == self.id:
                                paid_amount = paid_amount+z.debit_cash_basis
                else:
                    paid_amount = x.matched_debit_ids.amount
        # paid_amount = sum([x.amount for x in current_invoice.payment_ids])
        diff = (current_invoice.amount_total - paid_amount)
        amount = round(diff, 2)
        if current_invoice and amount <= 0:
            return True
        else:
            return False
