from odoo import api, SUPERUSER_ID
from odoo.addons.http_routing.models.ir_http import slugify


def migrate(cr, installed_version):
    env = api.Environment(cr, SUPERUSER_ID, {})

    # Migrate categories
    Category = env['request.category'].with_context(active_test=False)
    for record in Category.search([('code', '=', False)]):
        record.code = slugify(record.display_name, max_length=0)

    # Migrate stage types
    StageType = env['request.stage.type'].with_context(active_test=False)
    for record in StageType.search([('code', '=', False)]):
        record.code = slugify(record.display_name, max_length=0)
