from odoo.tools.sql import column_exists


def migrate(cr, installed_version):
    if not column_exists(cr, 'request_request', 'author_id'):
        cr.execute("""
            ALTER TABLE request_request
            ADD COLUMN author_id INTEGER;

            UPDATE request_request r
            SET author_id=(
                SELECT partner_id
                FROM res_users u
                WHERE u.id=r.created_by_id);

            UPDATE request_request r
            SET partner_id=(SELECT parent_id
                FROM res_partner p
                WHERE p.id=r.author_id)
            WHERE r.partner_id IS NULL;
        """)
