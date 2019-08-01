from contextlib import contextmanager
from odoo.tests.common import SavepointCase
from odoo.tools.misc import mute_logger

try:
    # pylint: disable=unused-import
    from freezegun import freeze_time  # noqa
except ImportError:  # pragma: no cover
    import logging
    logging.getLogger(__name__).warn(
        "freezegun not installed. Tests will not work!")


@contextmanager
def disable_mail_auto_delete(env):
    def patched_method(self, vals):
        vals = dict(vals, auto_delete=False)
        return patched_method.origin(self, vals)
    env['mail.mail']._patch_method(
        'create', patched_method)

    yield

    env['mail.mail']._revert_method('create')


class AccessRulesFixMixin(object):

    @classmethod
    def setUpClass(cls):
        super(AccessRulesFixMixin, cls).setUpClass()

        # Fix access rules
        #
        # Deactivate rules created by modules that are not initialized to
        # prevent errors raised when rule use field defined in uninitialized
        # addon
        rule_ids = cls.env['ir.model.data'].search([
            ('model', '=', 'ir.rule'),
            ('module', 'not in', tuple(cls.env.registry._init_modules)),
        ]).mapped('res_id')
        cls.env['ir.rule'].browse(rule_ids).write({'active': False})


class RequestCase(AccessRulesFixMixin, SavepointCase):
    """Test request base
    """

    @classmethod
    def setUpClass(cls):
        super(RequestCase, cls).setUpClass()
        cls.general_category = cls.env.ref(
            'generic_request.request_category_demo_general')
        cls.resource_category = cls.env.ref(
            'generic_request.request_category_demo_resource')
        cls.tec_configuration_category = cls.env.ref(
            'generic_request.request_category_demo_technical_configuration')

        # Request type
        cls.simple_type = cls.env.ref('generic_request.request_type_simple')
        cls.sequence_type = cls.env.ref(
            'generic_request.request_type_sequence')
        cls.non_ascii_type = cls.env.ref(
            'generic_request.request_type_non_ascii')
        cls.access_type = cls.env.ref(
            'generic_request.request_type_access')

        # Stages
        cls.stage_draft = cls.env.ref(
            'generic_request.request_stage_type_simple_draft')
        cls.stage_sent = cls.env.ref(
            'generic_request.request_stage_type_simple_sent')
        cls.stage_confirmed = cls.env.ref(
            'generic_request.request_stage_type_simple_confirmed')
        cls.stage_rejected = cls.env.ref(
            'generic_request.request_stage_type_simple_rejected')
        cls.stage_new = cls.env.ref(
            'generic_request.request_stage_type_sequence_new')
        # Routes
        cls.route_draft_to_sent = cls.env.ref(
            'generic_request.request_stage_route_type_simple_draft_to_sent')
        cls.non_ascii_route_draft_to_sent = cls.env.ref(
            'generic_request.request_stage_route_type_non_ascii_draft_to_sent')

        # Requests
        cls.request_1 = cls.env.ref(
            'generic_request.request_request_type_simple_demo_1')
        cls.request_2 = cls.env.ref(
            'generic_request.request_request_type_access_demo_1')

        # Users
        cls.demo_user = cls.env.ref('base.user_demo')
        cls.request_user = cls.env.ref(
            'generic_request.user_demo_request')
        cls.request_manager = cls.env.ref(
            'generic_request.user_demo_request_manager')
        cls.request_manager_2 = cls.env.ref(
            'generic_request.user_demo_request_manager_2')

    def run(self, *args, **kwargs):
        # Hide unnecessary log output
        with mute_logger('odoo.models.unlink',
                         'odoo.addons.mail.models.mail_mail'):
            return super(RequestCase, self).run(*args, **kwargs)

    def _close_request(self, request, stage, response_text=False, user=None):
        if user is None:
            user = self.env.user

        close_route = self.env['request.stage.route'].sudo(user).search([
            ('request_type_id', '=', request.type_id.id),
            ('stage_to_id', '=', stage.id),
        ])
        close_route.ensure_one()
        wiz = self.env['request.wizard.close'].sudo(user).create({
            'request_id': request.id,
            'close_route_id': close_route.id,
            'response_text': response_text,
        })
        wiz.action_close_request()

        self.assertEqual(request.stage_id, stage)
        self.assertEqual(request.response_text, response_text)


class AccessRightsCase(AccessRulesFixMixin, SavepointCase):

    @classmethod
    def setUpClass(cls):
        super(AccessRightsCase, cls).setUpClass()
        cls.simple_type = cls.env.ref('generic_request.request_type_simple')

        # Users
        cls.demo_user = cls.env.ref('generic_request.user_demo_request')
        cls.demo_manager = cls.env.ref(
            'generic_request.user_demo_request_manager')

        # Envs
        cls.uenv = cls.env(user=cls.demo_user)
        cls.menv = cls.env(user=cls.demo_manager)

        # Request fields
        cls.request_fields = cls.env[
            'request.request'].fields_view_get()['fields']

        # Request Type
        cls.usimple_type = cls.uenv.ref('generic_request.request_type_simple')
        cls.msimple_type = cls.menv.ref('generic_request.request_type_simple')

        # Request category
        cls.ucategory_demo_general = cls.uenv.ref(
            'generic_request.request_category_demo_general')
        cls.mcategory_demo_general = cls.menv.ref(
            'generic_request.request_category_demo_general')

    def run(self, *args, **kwargs):
        # Hide unnecessary log output
        with mute_logger('odoo.models.unlink',
                         'odoo.addons.mail.models.mail_mail'):
            return super(AccessRightsCase, self).run(*args, **kwargs)
