import logging
import collections

from odoo import models, fields, api, tools, _, exceptions, SUPERUSER_ID
from odoo.osv import expression

_logger = logging.getLogger(__name__)


try:
    from html2text import HTML2Text
except ImportError as error:
    _logger.debug(error)

TRACK_FIELD_CHANGES = set((
    'stage_id', 'user_id', 'type_id', 'category_id', 'request_text',
    'partner_id'))
REQUEST_TEXT_SAMPLE_MAX_LINES = 3
KANBAN_READONLY_FIELDS = set(('type_id', 'stage_id', 'category_id'))


def html2text(html):
    """ covert html to text, ignoring images and tables
    """
    if not html:
        return ""

    ht = HTML2Text()
    ht.ignore_images = True
    ht.ignore_tables = True
    ht.ignore_emphasis = True
    ht.ignore_links = True
    return ht.handle(html)


class RequestRequest(models.Model):
    _name = "request.request"
    _inherit = [
        'mail.thread',
        'mail.activity.mixin'
    ]
    _description = 'Request'
    _order = 'date_created DESC'
    _needaction = True

    name = fields.Char(
        required=True, index=True, readonly=True, default="New",
        copy=False)
    help_html = fields.Html(
        "Help", related="type_id.help_html", readonly=True)
    category_help_html = fields.Html(related='category_id.help_html',
                                     readonly=True, string="Category help")
    stage_help_html = fields.Html(
        "Stage help", related="stage_id.help_html", readonly=True)
    instruction_html = fields.Html(related='type_id.instruction_html',
                                   readonly=True, string='Instruction')
    note_html = fields.Html(related='type_id.note_html',
                            readonly=True, string="Note")

    # Type and stage related fields
    type_id = fields.Many2one(
        'request.type', 'Type', ondelete='restrict',
        required=True, index=True, track_visibility='always')
    type_color = fields.Char(related="type_id.color")
    category_id = fields.Many2one(
        'request.category', 'Category', index=True,
        required=False, ondelete="restrict", track_visibility='onchange')
    stage_id = fields.Many2one(
        'request.stage', 'Stage', ondelete='restrict',
        required=True, index=True, track_visibility="onchange",
        copy=False)
    stage_type_id = fields.Many2one(
        'request.stage.type', related="stage_id.type_id", string="Stage Type",
        index=True, readonly=True, store=True)
    stage_bg_color = fields.Char(
        compute="_compute_stage_colors", string="Stage Background Color")
    stage_label_color = fields.Char(
        compute="_compute_stage_colors")
    last_route_id = fields.Many2one('request.stage.route', 'Last Route')
    closed = fields.Boolean(
        related='stage_id.closed', store=True, index=True, readonly=True)
    can_be_closed = fields.Boolean(
        compute='_compute_can_be_closed', readonly=True)

    # UI change restriction fields
    can_change_request_text = fields.Boolean(
        compute='_compute_can_change_request_text', readonly=True)
    can_change_assignee = fields.Boolean(
        compute='_compute_can_change_assignee', readonly=True)
    can_change_author = fields.Boolean(
        compute='_compute_can_change_author', readonly=True)
    next_stage_ids = fields.Many2many(
        'request.stage', compute="_compute_next_stage_ids", readonly=True)

    # Request data fields
    request_text = fields.Html(required=True)
    response_text = fields.Html(required=False)
    request_text_sample = fields.Text(
        compute="_compute_request_text_sample", track_visibility="always",
        string='Request text')

    # dates+ fields
    date_created = fields.Datetime(
        'Created', default=fields.Datetime.now, readonly=True, copy=False)
    date_closed = fields.Datetime('Closed', readonly=True, copy=False)
    date_assigned = fields.Datetime('Assigned', readonly=True, copy=False)
    date_moved = fields.Datetime('Moved', readonly=True, copy=False)
    created_by_id = fields.Many2one(
        'res.users', 'Created by', readonly=True, ondelete='restrict',
        default=lambda self: self.env.user,
        help="Request was created by this user", copy=False)
    moved_by_id = fields.Many2one(
        'res.users', 'Moved by', readonly=True, ondelete='restrict',
        copy=False)
    closed_by_id = fields.Many2one(
        'res.users', 'Closed by', readonly=True, ondelete='restrict',
        copy=False, help="Request was closed by this user")

    partner_id = fields.Many2one(
        'res.partner', 'Partner', track_visibility='onchange',
        ondelete='restrict', help="Partner related to this request")
    author_id = fields.Many2one(
        'res.partner', 'Author', index=True, required=True,
        ondelete='restrict',
        track_visibility='onchange',
        domain=[('is_company', '=', False)],
        default=lambda self: self.env.user.partner_id,
        help="Author of this request")
    user_id = fields.Many2one(
        'res.users', 'Assigned to',
        ondelete='restrict', track_visibility='onchange',
        help="User responsible for next action on this request.")

    message_discussion_ids = fields.One2many(
        'mail.message', 'res_id', string='Messages',
        compute="_compute_message_discussion_ids")

    instruction_visible = fields.Boolean(
        compute='_compute_instruction_visible', default=False)

    activity_date_deadline = fields.Date(compute_sudo=True)

    # Events
    request_event_ids = fields.One2many(
        'request.event', 'request_id', 'Events', readonly=True)
    request_event_count = fields.Integer(
        compute='_compute_request_event_count', readonly=True)

    _sql_constraints = [
        ('name_uniq',
         'UNIQUE (name)',
         'Request name must be unique.'),
    ]

    @api.multi
    @api.depends('message_ids')
    def _compute_message_discussion_ids(self):
        for request in self:
            request.message_discussion_ids = request.message_ids.filtered(
                lambda r: r.subtype_id == self.env.ref('mail.mt_comment'))

    @api.depends('stage_id', 'stage_id.type_id')
    def _compute_stage_colors(self):
        for rec in self:
            rec.stage_bg_color = rec.stage_id.res_bg_color
            rec.stage_label_color = rec.stage_id.res_label_color

    @api.depends('stage_id.route_out_ids.stage_to_id.closed')
    def _compute_can_be_closed(self):
        for record in self:
            can_be_closed = False
            for route in record.stage_id.route_out_ids:
                if route.close:
                    can_be_closed = True
                    break
            record.can_be_closed = can_be_closed

    @api.depends('request_event_ids')
    def _compute_request_event_count(self):
        for record in self:
            record.request_event_count = len(record.request_event_ids)

    def _hook_can_change_request_text(self):
        """ Can be overridden in other addons
        """
        self.ensure_one()
        return not self.closed

    def _hook_can_change_assignee(self):
        """ Can be overridden in other addons
        """
        self.ensure_one()
        return not self.closed

    @api.depends('type_id', 'stage_id', 'user_id',
                 'partner_id', 'created_by_id')
    def _compute_can_change_request_text(self):
        for rec in self:
            rec.can_change_request_text = rec._hook_can_change_request_text()

    @api.depends('type_id', 'stage_id', 'user_id',
                 'partner_id', 'created_by_id')
    def _compute_can_change_assignee(self):
        for rec in self:
            rec.can_change_assignee = rec._hook_can_change_assignee()

    @api.depends('type_id', 'type_id.start_stage_id', 'stage_id')
    def _compute_can_change_author(self):
        for record in self:
            if not self.env.user.has_group(
                    'generic_request.group_request_user_can_change_author'):
                record.can_change_author = False
            elif record.stage_id != record.type_id.start_stage_id:
                record.can_change_author = False
            else:
                record.can_change_author = True

    def _get_next_stage_route_domain(self):
        self.ensure_one()
        return [
            ('request_type_id', '=', self.type_id.id),
            ('stage_from_id', '=', self.stage_id.id),
            ('close', '=', False)
        ]

    @api.depends('type_id', 'stage_id')
    def _compute_next_stage_ids(self):
        for record in self:
            routes = self.env['request.stage.route'].search(
                record._get_next_stage_route_domain())
            record.next_stage_ids = (
                record.stage_id + routes.mapped('stage_to_id'))

    @api.depends('request_text')
    def _compute_request_text_sample(self):
        for request in self:
            text_list = html2text(request.request_text).splitlines()
            result = []
            while len(result) <= REQUEST_TEXT_SAMPLE_MAX_LINES and text_list:
                line = text_list.pop(0)
                line = line.lstrip('#').strip()
                if not line:
                    continue
                result.append(line)
            request.request_text_sample = "\n".join(result)

    @api.depends('user_id')
    def _compute_instruction_visible(self):
        for rec in self:
            rec.instruction_visible = (
                (
                    self.env.user == rec.user_id or
                    self.env.user.id == SUPERUSER_ID or
                    self.env.user.has_group(
                        'generic_request.group_request_manager')
                ) and (
                    rec.instruction_html
                )
            )

    def _create_update_from_type(self, vals):
        r_type = self.env['request.type'].browse(vals['type_id'])

        # Name update
        if vals.get('name') == "###new###":
            # To set correct name for request generated from mail aliases
            # See code `mail.models.mail_thread.MailThread.message_new` - it
            # attempts to set name if it is empty. So we pass special name in
            # our method overload, and handle it here, to keep all request name
            # related logic in one place
            vals['name'] = False
        if not vals.get('name') and r_type.sequence_id:
            vals['name'] = r_type.sudo().sequence_id.next_by_id()
        elif not vals.get('name'):
            vals['name'] = self.env['ir.sequence'].sudo().next_by_code(
                'request.request.name')

        # Update stage
        if r_type.start_stage_id:
            vals['stage_id'] = r_type.start_stage_id.id
        else:
            raise exceptions.ValidationError(
                _("Cannot create request of type '%s':"
                  " This type have no start stage defined!") % r_type.name)
        return vals

    @api.model
    def _add_missing_default_values(self, values):
        res = super(RequestRequest, self)._add_missing_default_values(values)

        if res.get('author_id') and 'partner_id' not in values:
            author = self.env['res.partner'].browse(res['author_id'])
            if author.commercial_partner_id != author:
                res['partner_id'] = author.commercial_partner_id.id

        return res

    @api.model
    def create(self, vals):
        # Update date_assigned
        if vals.get('user_id'):
            vals.update({
                'date_assigned': fields.Datetime.now(),
            })

        if vals.get('type_id', False):
            vals = self._create_update_from_type(vals)

        if not vals.get('author_id') and vals.get('created_by_id'):
            create_user = self.env['res.users'].sudo().browse(
                vals['created_by_id'])
            vals.update({
                'author_id': create_user.partner_id.id,
            })

        self_ctx = self.with_context(mail_create_nolog=True)
        request = super(RequestRequest, self_ctx).create(vals)
        request.trigger_event('created')
        return request

    @api.multi
    def _get_changed_fields(self, field_names, vals):
        """ Preprocess vals to be written, and gether field changes
        """
        changes = collections.defaultdict(dict)
        changed_fields = set(field_names) & set(vals.keys())
        if changed_fields:
            # changes = {
            #     record_id: {
            #         field1: (old_value, new_value),
            #     }
            # }
            for record in self:
                for field in changed_fields:
                    old_value = record[field]
                    new_value = self._fields[field].convert_to_record(
                        self._fields[field].convert_to_cache(
                            vals[field], self),
                        self)
                    if old_value != new_value:
                        changes[record.id][field] = (old_value,
                                                     new_value)
        return dict(changes)

    @api.multi
    def _preprocess_write_changes(self, changes):
        """ Called before write

            This method may be overridden by other addons to add
            some preprocessing of changes, before write

            :param dict changes: keys are changed field names,
                                 values are tuples (old_value, new_value)
            :rtype: dict
            :return: values to update request with.
                     These values will be written just after write
        """
        Route = self.env['request.stage.route']

        self.ensure_one()
        vals = {}
        if 'user_id' in changes:
            new_user = changes['user_id'][1]  # (old_user, new_user)
            if new_user:
                vals['date_assigned'] = fields.Datetime.now()
            else:
                vals['date_assigned'] = False

        if 'stage_id' in changes:
            old_stage, new_stage = changes['stage_id']
            route = Route.ensure_route(self, new_stage.id)
            route.hook_before_stage_change(self)
            vals['last_route_id'] = route.id
            vals['date_moved'] = fields.Datetime.now()
            vals['moved_by_id'] = self.env.user.id

            if not old_stage.closed and new_stage.closed:
                vals['date_closed'] = fields.Datetime.now()
                vals['closed_by_id'] = self.env.user.id
            elif old_stage.closed and not new_stage.closed:
                vals['date_closed'] = False
                vals['closed_by_id'] = False

        if 'type_id' in changes:
            raise exceptions.ValidationError(_(
                'It is not allowed to change request type'))
        if 'category_id' in changes:
            raise exceptions.ValidationError(_(
                'It is not allowed to change request category'))

        return vals

    @api.multi
    def _postprocess_write_changes(self, changes):
        """ Called after write

            This method may be overridden by other modules to add
            some postprocessing of write.
            This method does not return any  value.

            :param dict changes: keys are changed field names,
                                 values are tuples (old_value, new_value)
            :return: None

        """

        self.ensure_one()
        if 'stage_id' in changes:
            self.last_route_id.hook_after_stage_change(self)

            # Trigger stage-change related events
            old_stage, new_stage = changes['stage_id']
            event_data = {
                'route_id': self.last_route_id.id,
                'old_stage_id': old_stage.id,
                'new_stage_id': new_stage.id,
            }
            if new_stage.closed and not old_stage.closed:
                self.trigger_event('closed', event_data)
            elif old_stage.closed and not new_stage.closed:
                self.trigger_event('reopened', event_data)
            else:
                self.trigger_event('stage-changed', event_data)

        if 'user_id' in changes:
            # Trigger assign-related events
            old_user, new_user = changes['user_id']
            event_data = {
                'old_user_id': old_user.id, 'new_user_id': new_user.id}
            if not old_user and new_user:
                self.trigger_event('assigned', event_data)
            elif old_user and new_user:
                self.trigger_event('reassigned', event_data)
            elif old_user and not new_user:
                self.trigger_event('unassigned', event_data)

        if 'request_text' in changes:
            old_text, new_text = changes['request_text']
            self.trigger_event('changed', {
                'old_text': old_text,
                'new_text': new_text})

    @api.multi
    def write(self, vals):
        changes = self._get_changed_fields(TRACK_FIELD_CHANGES, vals)

        # Store here updates got from preprocessing
        updates = collections.defaultdict(dict)

        for request in self:
            if request.id in changes:
                updates[request.id] = self._preprocess_write_changes(
                    changes[request.id])

        res = super(RequestRequest, self).write(vals)

        for request in self:
            if request.id in updates:
                super(RequestRequest, request).write(updates[request.id])
            if request.id in changes:
                request._postprocess_write_changes(changes[request.id])
        return res

    @api.multi
    def _track_subtype(self, init_values):
        """ Give the subtypes triggered by the changes on the record according
        to values that have been updated.

        :param init_values: the original values of the record;
                            only modified fields are present in the dict
        :type init_values: dict
        :returns: a subtype xml_id or False if no subtype is triggered
        """
        self.ensure_one()
        if 'stage_id' in init_values:
            init_stage = init_values['stage_id']
            if not init_stage and \
                    self.stage_id == self.type_id.start_stage_id:
                return 'generic_request.mt_request_created'
            if init_stage and init_stage != self.stage_id and \
                    self.stage_id.closed and not init_stage.closed:
                return 'generic_request.mt_request_closed'
            if init_stage and init_stage != self.stage_id and \
                    not self.stage_id.closed and init_stage.closed:
                return 'generic_request.mt_request_reopened'
            if init_stage != self.stage_id:
                return 'generic_request.mt_request_stage_changed'

        return 'generic_request.mt_request_updated'

    @api.onchange('type_id')
    def onchange_type_id(self):
        """ Set default stage_id
        """
        for request in self:
            if request.type_id and request.type_id.start_stage_id:
                request.stage_id = request.type_id.start_stage_id
            else:
                request.stage_id = self.env['request.stage'].browse([])

            if request.type_id and request.type_id.default_request_text:
                request.request_text = request.type_id.default_request_text

    @api.onchange('type_id')
    def _onchange_category_type(self):
        # TODO: rename to `_onchange_type_category`
        if self.category_id:
            # Clear category if it does not in allowed categs for selected type
            # Or if request type is not selected
            if not self.type_id:
                self.category_id = False
            elif self.category_id not in self.type_id.category_ids:
                self.category_id = False

        if self.type_id:
            return {
                'domain': {
                    'category_id': [
                        ('request_type_ids', '=', self.type_id.id),
                    ],
                },
            }

        return {
            'domain': {
                # When type is not selected category could not be selected too
                'category_id': expression.FALSE_DOMAIN,
            },
        }

    @api.onchange('author_id')
    def _onchange_author_id(self):
        for rec in self:
            if rec.author_id:
                rec.partner_id = self.author_id.parent_id
            else:
                rec.partner_id = False

    @api.model
    def fields_view_get(self, view_id=None, view_type='form',
                        toolbar=False, submenu=False):
        result = super(RequestRequest, self).fields_view_get(
            view_id=view_id, view_type=view_type,
            toolbar=toolbar, submenu=submenu)

        # Make type_id and stage_id readonly for kanban mode.
        # this is required to disable kanban drag-and-drop features for this
        # fields, because changing request type or request stage in this way,
        # may lead to broken workflow for requests (no routes to move request
        # to next stage)
        if view_type == 'kanban':
            for rfield in KANBAN_READONLY_FIELDS:
                if rfield in result['fields']:
                    result['fields'][rfield]['readonly'] = True
        return result

    @api.multi
    def ensure_can_assign(self):
        self.ensure_one()
        if self.closed:
            raise exceptions.UserError(
                _("You can not assign this request, "
                  "because this request is closed."))
        if not self.can_change_assignee:
            raise exceptions.UserError(
                _("You can not assign this request"))

    @api.multi
    def action_request_assign(self):
        self.ensure_one()
        self.ensure_can_assign()
        action = self.env.ref('generic_request.action_request_wizard_assign')
        action = action.read()[0]
        action['context'] = {
            'default_request_id': self.id,
        }
        return action

    # Default notifications
    def _send_default_notification__get_email_from(self, **kw):
        """ To be overloaded to change 'email_from' field for notifications
        """
        return False

    def _send_default_notification__get_context(self, event):
        """ Compute context for default notification
        """
        values = event.get_context()
        values.update({
            'company': self.env.user.company_id,
        })
        return values

    def _send_default_notification__get_msg_params(self, **kw):
        return dict(
            composition_mode='mass_mail',
            auto_delete=True,
            auto_delete_message=False,
            parent_id=False,  # override accidental context defaults
            subtype_id=self.env.ref('mail.mt_note').id,
            **kw,
        )

    def _send_default_notification__send(self, template, partners,
                                         event, **kw):
        """ Send default notification

            :param str template: XMLID of template to use for notification
            :param Recordset partners: List of partenrs that have to receive
                                       this notification
            :param Recordset event: Single record of 'request.event'
            :param function lazy_subject: function (self) that have to return
                                          translated string for subject
                                          for notification
        """
        values_g = self._send_default_notification__get_context(event)
        message_data_g = self._send_default_notification__get_msg_params(**kw)
        email_from = self._send_default_notification__get_email_from(**kw)
        if email_from:
            message_data_g['email_from'] = email_from

        # In order to handle translatable subjects, we use specific argument:
        # lazy_subject, which is function that receives 'self' and returns
        # string.
        lazy_subject = message_data_g.pop('lazy_subject', None)

        for partner in partners.sudo():
            # Skip partners without emails to avoid errors
            if not partner.email:
                continue
            values = dict(
                values_g,
                partner=partner,
            )
            self_ctx = self.sudo()
            if partner.lang:
                self_ctx = self_ctx.with_context(lang=partner.sudo().lang)
            message_data = dict(
                message_data_g,
                partner_ids=[(4, partner.id)],
                values=values)
            if lazy_subject:
                message_data['subject'] = lazy_subject(self_ctx)
            self_ctx.message_post_with_view(
                template,
                **message_data)

    def _send_default_notification_created(self, event):
        if not self.sudo().type_id.send_default_created_notification:
            return

        self._send_default_notification__send(
            'generic_request.message_request_created__author',
            self.sudo().author_id,
            event,
            lazy_subject=lambda self: _(
                "Request %s successfully created!") % self.name,
        )

    def _send_default_notification_assigned(self, event):
        if not self.sudo().type_id.send_default_assigned_notification:
            return

        self._send_default_notification__send(
            'generic_request.message_request_assigned__assignee',
            event.sudo().new_user_id.partner_id,
            event,
            lazy_subject=lambda self: _(
                "You have been assigned to request %s!") % self.name,
        )

    def _send_default_notification_closed(self, event):
        if not self.sudo().type_id.send_default_closed_notification:
            return

        self._send_default_notification__send(
            'generic_request.message_request_closed__author',
            self.sudo().author_id,
            event,
            lazy_subject=lambda self: _(
                "Your request %s has been closed!") % self.name,
        )

    def _send_default_notification_reopened(self, event):
        if not self.sudo().type_id.send_default_reopened_notification:
            return

        self._send_default_notification__send(
            'generic_request.message_request_reopened__author',
            self.sudo().author_id,
            event,
            lazy_subject=lambda self: _(
                "Your request %s has been reopened!") % self.name,
        )

    def handle_request_event(self, event):
        """ Place to handle request events
        """
        if event.event_type_id.code in ('assigned', 'reassigned'):
            self._send_default_notification_assigned(event)
        elif event.event_type_id.code == 'created':
            self._send_default_notification_created(event)
        elif event.event_type_id.code == 'closed':
            self._send_default_notification_closed(event)
        elif event.event_type_id.code == 'reopened':
            self._send_default_notification_reopened(event)

    def trigger_event(self, event_type, event_data=None):
        """ Trigger an event.

            :param str event_type: code of event type
            :param dict event_data: dictionary with data to be written to event
        """
        event_type_id = self.env['request.event.type'].get_event_type_id(
            event_type)
        event_data = event_data if event_data is not None else {}
        event_data.update({
            'event_type_id': event_type_id,
            'request_id': self.id,
            'user_id': self.env.user.id,
            'date': fields.Datetime.now(),
        })
        event = self.env['request.event'].sudo().create(event_data)
        self.handle_request_event(event)

    def get_mail_url(self):
        """ Get request URL to be used in mails
        """
        return "/mail/view/request/%s" % self.id

    @api.multi
    def _notify_get_groups(self, message, groups):
        """ Use custom url for *button_access* in notification emails
        """
        self.ensure_one()
        groups = super(RequestRequest, self)._notify_get_groups(
            message, groups)

        view_title = _('View Request')
        access_link = self.get_mail_url()

        # pylint: disable=unused-variable
        for group_name, group_method, group_data in groups:
            group_data['button_access'] = {
                'title': view_title,
                'url': access_link,
            }

        return groups

    def _message_auto_subscribe_followers(self, updated_values,
                                          default_subtype_ids):
        res = super(RequestRequest, self)._message_auto_subscribe_followers(
            updated_values, default_subtype_ids)

        if updated_values.get('author_id'):
            author = self.env['res.partner'].browse(
                updated_values['author_id'])
            if author.active:
                res.append((
                    author.id, default_subtype_ids, False))
        return res

    @api.multi
    def _message_auto_subscribe_notify(self, partner_ids, template):
        # Disable sending mail to assigne, when request was assigned.
        # See _postprocess_write_changes
        return super(
            RequestRequest,
            self.with_context(mail_auto_subscribe_no_notify=True)
        )._message_auto_subscribe_notify(partner_ids, template)

    @api.model
    def message_new(self, msg, custom_values=None):
        """ Overrides mail_thread message_new that is called by the mailgateway
            through message_process.
            This override updates the document according to the email.
        """
        custom_values = custom_values if custom_values is not None else {}

        # Concatenate subject and body for request text
        request_text_tmpl = "<h1>%(subject)s</h1>\n<br/>\n<br/>%(body)s"
        request_text = request_text_tmpl % {
            'subject': msg.get('subject', _("No Subject")),
            'body': msg.get('body', '')
        }

        # Compute defaults
        defaults = {
            'request_text': request_text,
            'name': "###new###",  # Special name to avoid
                                  # placing subject to as name
        }

        # Update defaults with partner and created_by_id if possible
        author_id = msg.get('author_id')
        if author_id:
            author = self.env['res.partner'].browse(author_id)
            defaults['partner_id'] = author.commercial_partner_id.id
            if len(author.user_ids) == 1:
                defaults['created_by_id'] = author.user_ids[0].id
            else:
                defaults['author_id'] = author.id
        else:
            author = False

        defaults.update(custom_values)

        request = super(RequestRequest, self).message_new(
            msg, custom_values=defaults)

        # Find partners from email and subscribe them
        email_list = tools.email_split(
            (msg.get('to') or '') + ',' + (msg.get('cc') or ''))
        partner_ids = request._find_partner_from_emails(
            email_list, force_create=False)
        partner_ids = [pid for pid in partner_ids if pid]

        if author:
            partner_ids += [author.id]

        request.message_subscribe(partner_ids)
        return request

    def action_show_request_events(self):
        self.ensure_one()
        action = self.env.ref(
            'generic_request.action_request_event_view').read()[0]
        action['domain'] = [('request_id', '=', self.id)]
        return action
