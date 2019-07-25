from odoo import models, fields, api, tools


class RequestEventType(models.Model):
    _name = "request.event.type"
    _description = "Request Event Type"
    _log_access = False

    name = fields.Char(required=True, translate=True)
    code = fields.Char(required=True)

    _sql_constraints = [
        ('code_ascii_only',
         r"CHECK (code ~ '^[a-zA-Z0-9\-_]*$')",
         'Code must be ascii only'),
        ('name_uniq',
         'UNIQUE (name)',
         'Name must be unique.'),
        ('code_uniq',
         'UNIQUE (code)',
         'Code must be unique.'),
    ]

    @api.model
    @tools.ormcache('code')
    def get_event_type_id(self, code):
        record = self.search(
            [('code', '=', code)], limit=1)
        if record:
            return record.id
        return False

    def get_event_type(self, code):
        event_type_id = self.get_event_type_id(code)
        if event_type_id:
            return self.browse(event_type_id)
        return self.browse()
