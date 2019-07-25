from odoo import exceptions
from odoo.osv import expression

from .common import RequestCase, freeze_time
from ..models.request_request import html2text


class TestRequestBase(RequestCase):
    """Test request base
    """

    def test_090_type_counters(self):
        access_type = self.env.ref(
            'generic_request.request_type_access')
        self.assertEqual(access_type.stage_count, 4)
        self.assertEqual(access_type.route_count, 3)

    def test_100_stage_previous_stage_ids(self):
        self.assertEqual(
            self.stage_draft.previous_stage_ids,
            self.stage_rejected)
        self.assertEqual(
            self.stage_sent.previous_stage_ids,
            self.stage_draft)
        self.assertEqual(
            self.stage_confirmed.previous_stage_ids,
            self.stage_sent)
        self.assertEqual(
            self.stage_rejected.previous_stage_ids,
            self.stage_sent)

    def test_110_stage_route_display_name_noname(self):
        self.route_draft_to_sent.name = False
        self.non_ascii_route_draft_to_sent.name = False

        self.assertEqual(
            self.route_draft_to_sent.display_name,
            "Draft -> Sent")

        self.assertEqual(
            self.non_ascii_route_draft_to_sent.display_name,
            u"Чорновик -> Відправлено")

    def test_115_stage_route_display_name_name(self):
        self.assertEqual(
            self.route_draft_to_sent.display_name,
            "Draft -> Sent [Send]")

    def test_117_stage_route_display_name_name_only(self):
        self.assertEqual(
            self.route_draft_to_sent.with_context(name_only=True).display_name,
            "Send")

    def test_117_stage_route_display_name_name_only_no_name(self):
        self.route_draft_to_sent.name = False
        self.assertEqual(
            self.route_draft_to_sent.with_context(name_only=True).display_name,
            "Draft -> Sent")

    def test_120_route_ensure_route__draft_sent(self):
        Route = self.env['request.stage.route']
        route = Route.ensure_route(
            self.request_1, self.stage_sent.id)
        self.assertTrue(route)
        self.assertEqual(len(route), 1)

    def test_125_route_ensure_route__draft_confirmed(self):
        Route = self.env['request.stage.route']

        with self.assertRaises(exceptions.ValidationError):
            Route.ensure_route(self.request_1, self.stage_confirmed.id)

    def test_130_request_create_simple(self):
        Request = self.env['request.request']

        request = Request.create({
            'type_id': self.simple_type.id,
            'category_id': self.general_category.id,
            'request_text': 'Request Text',
        })

        self.assertTrue(request.name.startswith('Req-'))
        self.assertEqual(request.stage_id, self.stage_draft)

    def test_135_request_create_and_assign(self):
        Request = self.env['request.request']

        request = Request.create({
            'type_id': self.simple_type.id,
            'category_id': self.general_category.id,
            'request_text': 'Request Text',
            'user_id': self.request_manager.id,
        })

        self.assertEqual(request.user_id, self.request_manager)
        self.assertTrue(request.date_assigned)

    def test_140_request_write_stage_sent(self):
        self.assertEqual(self.request_1.stage_id, self.stage_draft)

        self.request_1.write({'stage_id': self.stage_sent.id})

        self.assertEqual(self.request_1.stage_id, self.stage_sent)

    def test_145_request_write_stage_confirmed(self):
        self.assertEqual(self.request_1.stage_id, self.stage_draft)

        with self.assertRaises(exceptions.ValidationError):
            self.request_1.write({'stage_id': self.stage_confirmed.id})

    def test_150_request_type_sequence(self):
        Request = self.env['request.request']

        request = Request.create({
            'type_id': self.sequence_type.id,
            'category_id': self.resource_category.id,
            'request_text': 'Request Text',
        })

        self.assertTrue(request.name.startswith('RSR-'))
        self.assertEqual(request.stage_id, self.stage_new)

    def test_155_request__type_changed(self):
        Request = self.env['request.request']

        # Create new (empty) request
        request = Request.new({})
        self.assertFalse(request.stage_id)
        self.assertFalse(request.type_id)

        # Run onchange type_id:
        request.onchange_type_id()
        self.assertFalse(request.stage_id)
        self.assertFalse(request.type_id)

        request.type_id = self.simple_type
        self.assertFalse(request.stage_id)
        self.assertEqual(request.type_id, self.simple_type)

        request.onchange_type_id()
        self.assertEqual(request.stage_id, self.stage_draft)
        self.assertEqual(request.type_id, self.simple_type)

    def test_157_request__type_changed_restricts_category(self):
        Request = self.env['request.request']

        category_tech = self.env.ref(
            'generic_request.request_category_demo_technical_configuration')

        # Create new (empty) request
        request = Request.new({})
        self.assertFalse(request.stage_id)
        self.assertFalse(request.type_id)

        request.onchange_type_id()

        res = request._onchange_category_type()
        self.assertFalse(request.stage_id)
        self.assertFalse(request.type_id)
        self.assertFalse(request.category_id)

        # This domain have to disallow category selection when request type is
        # not selected
        self.assertEqual(res['domain']['category_id'], expression.FALSE_DOMAIN)

        # Choose request type 'Grant Access'
        request.type_id = self.access_type
        request.onchange_type_id()
        self.assertEqual(request.stage_id, self.access_type.start_stage_id)

        res = request._onchange_category_type()
        self.assertFalse(request.category_id)
        self.assertEqual(
            res['domain']['category_id'],
            [('request_type_ids', '=', self.access_type.id)])

        # Choose category Demo / Technical / Configuration
        self.assertIn(self.access_type, category_tech.request_type_ids)
        request.category_id = category_tech

        # Change request type to *Запит на встановлення ОС* which have same
        # related categories, and ensure, that category not changed, but domain
        # changed
        request.type_id = self.non_ascii_type

        request.onchange_type_id()
        self.assertEqual(request.stage_id, self.non_ascii_type.start_stage_id)

        res = request._onchange_category_type()
        self.assertTrue(request.category_id)
        self.assertEqual(
            res['domain']['category_id'],
            [('request_type_ids', '=', self.non_ascii_type.id)])
        self.assertIn(self.non_ascii_type, category_tech.request_type_ids)
        self.assertEqual(request.category_id, category_tech)

        # Change reqyest type to *Simple request*, which have different
        # categories available, and ensure, that category set to null.
        request.type_id = self.simple_type

        request.onchange_type_id()
        self.assertEqual(request.stage_id, self.simple_type.start_stage_id)

        res = request._onchange_category_type()
        self.assertFalse(request.category_id)
        self.assertEqual(
            res['domain']['category_id'],
            [('request_type_ids', '=', self.simple_type.id)])
        self.assertNotIn(self.simple_type, category_tech.request_type_ids)

    def test_160_request_category_display_name(self):

        self.assertEqual(
            self.tec_configuration_category.display_name,
            u"Demo / Technical / Configuration")

    def test_170_request_type_category_change(self):
        request = self.env['request.request'].create({
            'type_id': self.simple_type.id,
            'category_id': self.resource_category.id,
            'request_text': 'test',
        })

        with self.assertRaises(exceptions.ValidationError):
            request.write({'type_id': self.sequence_type.id})

        with self.assertRaises(exceptions.ValidationError):
            request.write({'category_id': self.tec_configuration_category.id})

    def test_180_request_close_via_wizard(self):
        request = self.env.ref(
            'generic_request.request_request_type_sequence_demo_1')
        request.stage_id = self.env.ref(
            'generic_request.request_stage_type_sequence_sent')

        close_stage = self.env.ref(
            'generic_request.request_stage_type_sequence_closed')
        close_route = self.env.ref(
            'generic_request.request_stage_route_type_sequence_sent_to_closed')

        request.response_text = 'test response 1'

        request_closing = self.env['request.wizard.close'].create({
            'request_id': request.id,
            'close_route_id': close_route.id,
        })
        request_closing.onchange_request_id()
        self.assertEqual(request_closing.response_text, request.response_text)
        self.assertEqual(request_closing.response_text,
                         '<p>test response 1</p>')

        request_closing.close_route_id = close_route
        request_closing.response_text = 'test response 42'
        request_closing.action_close_request()

        self.assertEqual(request.stage_id, close_stage)
        self.assertEqual(request.response_text, '<p>test response 42</p>')

    def test_request_html2text(self):
        self.assertEqual(html2text(False), "")
        self.assertEqual(html2text(None), "")
        self.assertEqual(
            html2text("<h1>Test</h1>").strip(), "# Test")

    def test_190_type_default_stages(self):
        type_default_stages = self.env['request.type'].with_context(
            create_default_stages=True).create({
                'name': "test-default-stages",
                'code': "test-default-stages",
            })
        self.assertEqual(type_default_stages.route_count, 1)
        self.assertEqual(
            type_default_stages.route_ids.stage_from_id.name, 'New')
        self.assertEqual(
            type_default_stages.route_ids.stage_to_id.name, 'Closed')

    def test_200_type_no_default_stages(self):
        type_no_default_stages = self.env['request.type'].create({
            'name': "test-no-default-stages",
            'code': "test-no-default-stages",
        })
        self.assertEqual(type_no_default_stages.route_count, 0)
        self.assertEqual(len(type_no_default_stages.stage_ids), 0)

        with self.assertRaises(exceptions.ValidationError):
            self.env['request.request'].create({
                'type_id': type_no_default_stages.id,
                'request_text': 'test',
            })

    def test_210_test_kaban_readonly_fields(self):
        res = self.env['request.request'].fields_view_get(view_type='kanban')
        self.assertTrue(res['fields']['type_id']['readonly'])
        self.assertTrue(res['fields']['stage_id']['readonly'])
        self.assertTrue(res['fields']['category_id']['readonly'])

    def test_220_delete_stage_with_routes(self):
        with self.assertRaises(exceptions.ValidationError):
            self.stage_confirmed.unlink()

    def test_230_delete_stage_without_routes(self):
        stage = self.env['request.stage'].create({
            'name': 'Test',
            'code': 'test',
            'request_type_id': self.simple_type.id,
        })
        stage.unlink()  # no errors raised

    def test_240_request_events(self):
        with freeze_time('2018-07-09'):
            request = self.env['request.request'].create({
                'type_id': self.simple_type.id,
                'request_text': 'Test',
            })
            self.assertEqual(request.request_event_count, 1)
            self.assertEqual(
                request.request_event_ids.event_type_id.code, 'created')

        with freeze_time('2018-07-25'):
            # Change request text
            request.request_text = 'Test 42'

            # Check that new event generated
            self.assertEqual(request.request_event_count, 2)
            self.assertEqual(
                request.request_event_ids[0].event_type_id.code, 'changed')
            self.assertEqual(
                request.request_event_ids[0].old_text, '<p>Test</p>')
            self.assertEqual(
                request.request_event_ids[0].new_text, '<p>Test 42</p>')

            # Test autovacuum of events (by default 90 days old)
            # No events removed, date not changed
            cron_job = self.env.ref(
                'generic_request.ir_cron_request_vacuum_events')
            cron_job.method_direct_trigger()
            self.assertEqual(request.request_event_count, 2)

        with freeze_time('2018-08-09'):
            # Test autovacuum of events (by default 90 days old)
            # No events removed, events not older that 90 days
            cron_job = self.env.ref(
                'generic_request.ir_cron_request_vacuum_events')
            cron_job.method_direct_trigger()
            self.assertEqual(request.request_event_count, 2)

        with freeze_time('2018-10-19'):
            # Test autovacuum of events (by default 90 days old)
            # One events removed, created event is older that 90 days
            cron_job = self.env.ref(
                'generic_request.ir_cron_request_vacuum_events')
            cron_job.method_direct_trigger()
            self.assertEqual(request.request_event_count, 1)
            self.assertEqual(
                request.request_event_ids.event_type_id.code, 'changed')
            self.assertEqual(
                request.request_event_ids.old_text, '<p>Test</p>')
            self.assertEqual(
                request.request_event_ids.new_text, '<p>Test 42</p>')

        with freeze_time('2018-10-27'):
            # Test autovacuum of events (by default 90 days old)
            # All events removed, all events older that 90 days
            cron_job = self.env.ref(
                'generic_request.ir_cron_request_vacuum_events')
            cron_job.method_direct_trigger()
            self.assertEqual(request.request_event_count, 0)

    def test_unlink_just_created(self):
        request = self.env['request.request'].sudo(
            self.request_manager
        ).create({
            'type_id': self.simple_type.id,
            'request_text': 'test',
        })
        with self.assertRaises(exceptions.AccessError):
            request.unlink()

        # Managers with group *can delete requests* are allowed to delete
        # requests
        self.request_manager.groups_id |= self.env.ref(
            'generic_request.group_request_manager_can_delete_request')
        request.unlink()

    def test_unlink_processed(self):
        request = self.env['request.request'].sudo(
            self.request_manager
        ).create({
            'type_id': self.simple_type.id,
            'request_text': 'test',
        })
        request.request_text = 'test 42'
        request.user_id = self.request_manager

        with self.assertRaises(exceptions.AccessError):
            request.unlink()

        # Managers with group *can delete requests* are allowed to delete
        # requests
        self.request_manager.groups_id |= self.env.ref(
            'generic_request.group_request_manager_can_delete_request')
        request.unlink()
