from odoo import api, models, _
from odoo.exceptions import UserError


class Skit_PosSession(models.Model):
    _inherit = 'pos.session'

    def _confirm_paylater_orders(self, pay_later_order):
            """ Posting method for Pay later order while close session
            :param pay_later_order:order
             """
            for session in self:
                pay_order = pay_later_order.filtered(
                            lambda order: order.state in ['invoiced', 'done'])
                pay_order.sudo()._reconcile_payments()

    @api.multi
    def action_pos_session_close(self):
            # Close CashBox
            for session in self:
                company_id = session.config_id.company_id.id
                ctx = dict(self.env.context, force_company=company_id,
                           company_id=company_id)
                for st in session.statement_ids:
                    if abs(st.difference) > (
                                st.journal_id.amount_authorized_diff):
                        # The pos manager can close statements with maximums.
                        if not self.env['ir.model.access'].check_groups(
                                            "point_of_sale.group_pos_manager"):
                            raise UserError(_("Your ending balance is too \
                            different from the theoretical cash closing \
                            (%.2f), the maximum allowed is: %.2f. \
                            You can contact your manager to force it.") % (
                                    st.difference,
                                    (st.journal_id.amount_authorized_diff)))
                    if (st.journal_id.type not in ['bank', 'cash']):
                        raise UserError(_("The type of the journal for your \
                        payment method should be bank or cash "))
                    st.with_context(ctx).sudo().button_confirm_bank()
            account_statement_line = self.env[
                    'account.bank.statement.line'].search([
                            ('statement_id', 'in', session.statement_ids.ids)])
            self.with_context(ctx)._confirm_orders()
            for line in account_statement_line:
                if line.pos_statement_id.session_id.id != session.id:
                    pay_later_order = self.env['pos.order'].search([
                            ('id', '=', int(line.pos_statement_id.id)),
                            ('session_id', '!=', session.id)])
                    self.with_context(ctx)._confirm_paylater_orders(
                                                    pay_later_order)
            self.write({'state': 'closed'})
            return {
                'type': 'ir.actions.client',
                'name': 'Point of Sale Menu',
                'tag': 'reload',
                'params': {'menu_id': self.env.ref(
                                'point_of_sale.menu_point_root').id},
            }
