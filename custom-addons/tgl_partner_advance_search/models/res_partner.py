# -*- coding: utf-8 -*-

from odoo import api, fields, models, _
from odoo.exceptions import ValidationError, UserError
from odoo.osv.expression import get_unaccent_wrapper
from odoo.addons.base.models import res_partner
        
class ResPartner(models.Model):
    _inherit = 'res.partner'

    @api.model
    def name_search(self, name, args=None, operator='ilike', limit=100):
        if args is None:
            args = []
        if name and operator in ('=', 'ilike', '=ilike', 'like', '=like'):
            self.check_access_rights('read')
            where_query = self._where_calc(args)
            self._apply_ir_rules(where_query, 'read')
            from_clause, where_clause, where_clause_params = where_query.get_sql()
            where_str = where_clause and (" WHERE %s AND " % where_clause) or ' WHERE '

            # search on the name of the contacts and of its company
            search_name = name
            if operator in ('ilike', 'like'):
                search_name = '%%%s%%' % name
            if operator in ('=ilike', '=like'):
                operator = operator[1:]

            unaccent = get_unaccent_wrapper(self.env.cr)

            query = """SELECT id
                         FROM res_partner
                      {where} ({email} {operator} {percent}
                           OR {display_name} {operator} {percent}
                           OR {reference} {operator} {percent}
                           OR {phone} {operator} {percent}
                           OR {mobile} {operator} {percent})
                           -- don't panic, trust postgres bitmap
                     ORDER BY {display_name} {operator} {percent} desc,
                              {display_name}
                    """.format(where=where_str,
                               operator=operator,
                               email=unaccent('email'),
                               display_name=unaccent('display_name'),
                               reference=unaccent('ref'),
                               phone=unaccent('phone'),
                               mobile=unaccent('mobile'),
                               percent=unaccent('%s'))

            where_clause_params += [search_name]*6
            if limit:
                query += ' limit %s'
                where_clause_params.append(limit)
            self.env.cr.execute(query, where_clause_params)
            partner_ids = map(lambda x: x[0], self.env.cr.fetchall())

            if partner_ids:
                return self.browse(partner_ids).tgl_name_get()
            else:
                return []
        return self.search(args, limit=limit).tgl_name_get()

    @api.multi
    def tgl_name_get(self):
        res = []
        for partner in self:
            name = partner.name
            if partner.mobile:
                name += ' | ' + partner.mobile
            elif partner.phone:
                name += ' | ' + partner.phone
            if partner.email:
                name += ' | ' + partner.email
            if partner.comment:
                name += ' | ' + partner.comment
            res.append((partner.id, name))
        return res