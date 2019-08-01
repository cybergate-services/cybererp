# -*- coding: utf-8 -*-
import logging
from odoo import api, models, fields, _
from odoo.exceptions import UserError

_logger = logging.getLogger(__name__)


class account_journal(models.Model):
    _inherit = "account.journal"
    _description = "Checkbox for Pay Later"

    is_pay_later = fields.Boolean('Is Pay Later', default=False)

    @api.model
    def create(self, vals):
        """ Create New Records """
        company_id = vals.get('company_id') or self.company_id.id 
        account_ids = self.search([('company_id','=',company_id)]) # load the journal of self.company        
        for account in account_ids:
            if account.is_pay_later and vals.get('is_pay_later') is True:
                raise UserError(_('Pay Later is already selected for another journal. You cannot use it for multiple journals.'))
        res = super(account_journal, self).create(vals)
        return res

    @api.multi
    def write(self, vals):
        """ Update Records """

        company_id = vals.get('company_id') or self.company_id.id 
        account_ids = self.search([('company_id','=',company_id)]) # load the journal of self.company
        for account in account_ids:
            if account.is_pay_later and vals.get('is_pay_later') is True:
                raise UserError(_('Pay Later is already selected for another journal. You cannot use it for multiple journals.'))
        res = super(account_journal, self).write(vals)
        return res


class Skit_PosOrder(models.Model):
    _inherit = 'pos.order'

    def _reconcile_payments(self):
        """From this method restrict invoice status changed to Paid,
        only for the journal 'Pay Later'"""
        for order in self:
            aml = order.statement_ids.mapped(
                        'journal_entry_ids') | order.account_move.line_ids | (
                                            order.invoice_id.move_id.line_ids)
            aml = aml.filtered(lambda r: not r.reconciled and
                               r.account_id.internal_type == 'receivable' and
                               r.partner_id == (
                                    order.partner_id.commercial_partner_id))

            # Reconcile returns first
            # to avoid mixing up the credit of a
            # payment and the credit of a return
            # in the receivable account
            # aml_returns = aml.filtered(lambda l: (
            # l.journal_id.type == 'sale' and l.credit) or (
            # l.journal_id.type != 'sale' and l.debit))
            try:
                # Added to restrict invoice status change to paid
                aml.reconcile()
            #  aml_returns.reconcile()
            # (aml - aml_returns).reconcile()
            except:
                # There might be unexpected situations where the automatic
                # reconciliation won't
                # work. We don't want the user to be blocked because of this,
                # since the automatic
                # reconciliation is introduced for convenience, not for
                # mandatory accounting
                # reasons.
                _logger.error('Reconciliation did not work for order %s',
                              order.name)
                continue

    @api.model
    def fetch_partner_order(self, customer, session_id):
        """ Serialize the orders of the customer

        params: customer int representing the customer id
        """
        params = {'partner_id': customer}
        # Generate Order Details
        sql_query = """ select  x.order_id, x.date_order, x.type  from (
                        select id as order_id,date_order,'POS'as type
                        from pos_order
                        where partner_id = %(partner_id)s
                        )
                        as x order by x.date_order desc"""

        self._cr.execute(sql_query, params)
        rows = self._cr.dictfetchall()
        datas = self.get_order_datas(rows, session_id)
        idatas = self.get_pending_invoice(customer, session_id)

        result = {'orders': datas, 'pendinginvoice': idatas}
        return result

    @api.model
    def get_order_datas(self, rows, session_id):
        """ Serialize all orders of the devotee

        params: rows - list of orders
        """
        datas = []
        sno = 0
        pos_ids = [x['order_id'] for x in rows if x['type'] == "POS"]
        porders = self.env['pos.order'].search([('id', 'in', pos_ids)])
        allorders = {'POS': porders}
        for key, orders in allorders.items():
            for order in orders:
                sno = sno + 1
                dateorder = False
                invoices = self.env['account.invoice'].search([
                                        ('id', 'in', order.invoice_id.ids)])
                dateorder = fields.Date.from_string(order.date_order)
                session_id = order.session_id.id
                if dateorder:
                    dateorder = dateorder.strftime("%Y/%m/%d")
                else:
                    dateorder = ''
                if invoices:
                    for invoice in invoices:
                        datas.append({
                                'id': order.id,
                                'sno': sno,
                                'type': key,
                                'invoice_ref': invoice.number,
                                'invoice_id': invoice.id,
                                'amount_total': round(order.amount_total, 2),
                                'date_order': dateorder,
                                'name': order.name or '',
                                'session_id': session_id})
                else:
                    datas.append({'id': order.id,
                                  'sno': sno,
                                  'type': key,
                                  'invoice_ref': '',
                                  'invoice_id': '',
                                  'amount_total': round(order.amount_total, 2),
                                  'date_order': dateorder,
                                  'name': order.name or '',
                                  'session_id': session_id})
        return datas

    @api.model
    def get_pending_invoice(self, partner_id, session_id):
        """ Fetch the pending invoice for current user
        params: partner - current user
        """
        idatas = []

        p_invoice = self.env['account.invoice'].search(
                            [('partner_id', '=', partner_id),
                             ('type', 'not in', ('in_invoice', 'in_refund')),
                             ('state', '=', 'open')])
        isno = 0
        paid_amount = 0
        for invoice in p_invoice:
            isno = isno + 1
            posorder = self.env['pos.order'].search([
                                ('invoice_id', '=', invoice.id)])
            type = 'POS'
            paid_amount1 = 0
            paid_amount2 = 0
            if posorder:
                if posorder.statement_ids:
                    paid_amount1 = sum([x.amount for x in posorder.statement_ids if not x.journal_id.is_pay_later])
                account_payment = self.env['account.payment'].sudo().search(
                                       [('invoice_ids', 'in', invoice.id)])
                if account_payment:
                    paid_amount2 = sum([x.amount for x in account_payment if not x.journal_id.is_pay_later])
                paid_amount = paid_amount1 + paid_amount2
                dateinvoice = fields.Date.from_string(invoice.date_invoice)
                diff = (invoice.amount_total - paid_amount)
                amt = round(diff, 2)
                if diff == 0:
                    amt = 0
                idatas.append({'id': invoice.id,
                               'sno': isno,
                               'type': type,
                               'porder_id': posorder.id or '',
                               'name': invoice.origin or '',
                               'invoice_ref': invoice.number,
                               'amount_total': round(invoice.amount_total, 2),
                               'unpaid_amount': amt if amt > 0 else '',
                               'date_invoice': dateinvoice.strftime("%Y/%m/%d")
                               })
        return idatas

    @api.model
    def fetch_invoice_lines(self, invoice_id):
        """ Serialize the invoice Lines
        params: devotee int representing the invoice id
        """
        invoice = self.env['account.invoice'].browse(int(invoice_id))
        iLines = invoice.invoice_line_ids
        line = []
        sno = 0
        for iLine in iLines:
            sno = sno + 1
            line.append({
                'sno': sno,
                'id': iLine.id,
                'product': iLine.product_id.name,
                'qty': iLine.quantity,
                'price_unit': iLine.price_unit,
                'amount': iLine.price_subtotal
            })
        return line
    
    def add_payment(self, data):
        """ update the statement_id for pending invoice."""
        statement_id = super(Skit_PosOrder, self).add_payment(data)
        statement_lines = self.env['account.bank.statement.line'].search([('statement_id', '=', statement_id),
                                                                         ('pos_statement_id', '=', self.id),
                                                                         ('journal_id', '=', data['journal']),
                                                                         ('amount', '=', data['amount'])])

        for line in statement_lines:           
            if data.get('open_inv'):
                line.statement_id = data.get('statement_id')
                line.ref = data.get('ref')
        return statement_id

class Skit_AccountInvoice(models.Model):
    _inherit = 'account.invoice'

    is_pending_invoice = fields.Boolean('Current Invoice', default=False)

    @api.model
    def get_pending_invoice_details(self, invoice_id, payment_lines,
                                    pos_session):
        """ Get Invoice Details and payment process """
        for pl in payment_lines:
            invoice = self.browse(int(invoice_id))
            order = self.env['pos.order'].search([
                ('invoice_id', '=', invoice.id)])
            amount = (pl['amount'] - pl['change'])
            journal_id = pl['paymethod']['journal']['id']
            session = self.env['pos.session'].browse(int(pos_session))
            """  add payment methods for POS order under Payment tab
                create account.bank.statement.line  """
            journal_id = pl['paymethod']['journal']['id']
            session = self.env['pos.session'].browse(int(pos_session))
            current_date = fields.Date.from_string(fields.Date.today())
            for statement in session.statement_ids:
                if statement.journal_id.id == journal_id:
                    statement_id = statement.id
                    args = {
                            'amount': amount,
                            'date': current_date,
                            'name': pl['name'] + ': ',
                            'partner_id': invoice.partner_id.id or False,
                            'statement_id': statement_id,
                            'pos_statement_id': order.id,
                            'journal': journal_id,
                            'ref': pl['name'],
                            'open_inv': True
                    }
                    order.add_payment(args)
            invoice.update({'is_pending_invoice': True})
        return True
