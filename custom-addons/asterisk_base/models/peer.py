# -*- coding: utf-8 -*-

from datetime import datetime
import logging
import random
import string
from odoo import models, fields, api, _
from odoo.exceptions import ValidationError, UserError
try:
    import humanize
    HUMANIZE = True
except ImportError:
    HUMANIZE = False
from .utils import remove_empty_lines


logger = logging.getLogger(__name__)

DEFAULT_SECRET_LENGTH = 10
PEER_TYPES = [
    ('user', 'User'),
    ('trunk', 'Trunk'),
]
YESNO_VALUES = [('yes', 'Yes'), ('no', 'No')]


def _generate_secret(length=DEFAULT_SECRET_LENGTH):
    chars = string.ascii_letters + string.digits
    password = ''
    while True:
        password = ''.join(map(lambda x: random.choice(chars), range(length)))
        if filter(lambda c: c.isdigit(), password) and \
                filter(lambda c: c.isalpha(), password):
            break
    return password



class SipPeer(models.Model):
    _name = 'asterisk.sip_peer'
    _description = 'Asterisk SIP Peer'
    _order = 'write_date desc'

    server = fields.Many2one(comodel_name='asterisk.server', required=True)
    extension = fields.Char()
    extension_id = fields.One2many('asterisk.extension',
                                   inverse_name='sip_peer')
    user = fields.One2many(comodel_name='asterisk.user', inverse_name='peer',
                           readonly=True)
    user_extension = fields.Char(related='user.extension')
    extension_list = fields.Char(compute='_get_extension', store=True,
                                 string=_('Extension'))
    route_group = fields.Many2one('asterisk.outgoing_route_group',
                                  ondelete='restrict')
    user_route_group = fields.Many2one(related='user.route_group')
    # To display in tree view
    user_list = fields.Char(compute='_get_user_list', string=_('User'))
    name = fields.Char(size=80, index=True, required=True)
    note = fields.Char()
    peer_type = fields.Selection(selection=PEER_TYPES, index=True)
    peer_statuses = fields.One2many(comodel_name='asterisk.sip_peer_status',
                                    inverse_name='peer')
    peer_status_count = fields.Integer(compute='_get_peer_status_count',
                                       store=True, string='Events')
    # Asterisk fields
    accountcode = fields.Char(size=20)
    amaflags = fields.Char(size=40)
    callgroup = fields.Char(size=40)
    callerid = fields.Char(size=80, string='Caller ID')
    canreinvite = fields.Selection([('yes', 'Yes'), ('no', 'No')],
                                   size=3, string='Can reinvite', default='no')
    #context_id = fields.Many2one('asterisk.conf.extensions', ondelete='restrict')
    context = fields.Char(index=True, size=40)
    defaultip = fields.Char(size=15, string='Default IP')
    dtmfmode = fields.Selection(size=10, string='DTMF mode', required=True,
                           default='rfc2833', selection=[('auto', 'Auto'),
                            ('inband', 'Inband'), ('rfc2833', 'RFC2833'),
                            ('info', 'Info'), ('shortinfo', 'Short Info')])
    fromuser = fields.Char(size=80, string='From user')
    fromdomain = fields.Char(size=80, string='From domain')
    host = fields.Char(size=40)
    outboundproxy = fields.Char(size=80)
    insecure = fields.Selection(selection=[(x,x) for x in ('port', 'invite', 'port,invite')],
        help="""Port - Allow matching of peer by IP address without matching port number.
        Invite - Do not require authentication of incoming INVITEs.
        Port,Invite - Both (Not so rarely enabled for Trunks).""")
    language = fields.Char(size=2)
    mailbox = fields.Char(size=50)
    md5secret = fields.Char(size=80)
    nat = fields.Char(selection=[('no', 'No'), ('force_rport', 'Force rport'),
                             ('comedia', 'Comedia'),
                             ('auto_force_rport', 'Auto force rport'),
                             ('auto_comedia', 'Auto comedia'),
                             ('force_rport,comedia', 'Force rport, Comedia')],
                      size=64, default='force_rport,comedia')
    permit = fields.Char(size=95)
    deny = fields.Char(size=95)
    mask = fields.Char(size=95)
    pickupgroup = fields.Char(size=10)
    port = fields.Integer()
    qualify = fields.Char(size=5)
    restrictcid = fields.Char(size=1)
    rtptimeout = fields.Integer(string='RTP timeout')
    rtpholdtimeout = fields.Integer(string='RTP hold timeout')
    secret = fields.Char(size=80, default=lambda x: _generate_secret())
    remotesecret = fields.Char(size=40,
        help="The password we use to authenticate to them. Specify only when different from Secret.")
    type = fields.Selection(selection=[('user', 'User'), ('peer', 'Peer'),
                                       ('friend', 'Friend')], required=True,
                                                              default='friend')
    disallow = fields.Char(size=100)
    allow = fields.Char(size=100, default='all')
    musiconhold = fields.Char(size=100, string='Music on hold')
    regcontext = fields.Char(size=80)
    cancallforward = fields.Char(size=3, default='yes')    
    lastms = fields.Integer()
    defaultuser = fields.Char(size=80, string='Default user')
    subscribecontext = fields.Char(size=80)
    regserver = fields.Char(size=80)
    callbackextension = fields.Char(size=250)
    transport = fields.Selection(selection=[(x,x) for x in
        ('udp', 'tcp', 'tls', 'ws', 'wss', 'udp,tcp', 'tcp,udp')])
    directmedia = fields.Selection(selection=[(x,x) for x in
        ('yes', 'no', 'nonat', 'update')], default='nonat')
    trustrpid = fields.Selection(selection=YESNO_VALUES,
        help="If Remote-Party-ID should be trusted")
    progressinband = fields.Selection(selection=[
        ('yes', 'Yes'),
        ('no', 'No'),
        ('never', 'Never')], help="If we should generate in-band ringing")
    promiscredir = fields.Selection(selection=YESNO_VALUES,
        help="If yes, allows 302 or REDIR to non-local SIP address")
    setvar = fields.Char(size=200,
        help="Channel variable to be set for all calls from or to this device")
    callcounter = fields.Selection(selection=YESNO_VALUES,
        help="Enable call counters on devices. Can be set for all in [general] section")
    busylevel = fields.Integer(help="""If you set the busylevel,
        we will indicate busy when we have a number of calls that matches the busylevel threshold.""")
    allowoverlap = fields.Selection(selection=[('yes', 'Yes'), ('no', 'No'), ('dtmf', 'DTMF')],
        help="RFC3578 overlap dialing support. (Default is yes)")
    allowsubscribe = fields.Selection(selection=YESNO_VALUES,
        help="Support for subscriptions. (Default is yes)")
    videosupport = fields.Selection(selection=YESNO_VALUES,
        help="""Support for SIP video.
        You MUST enable it in [general] section to turn this on per user.""")
    maxcallbitrate = fields.Integer(help="Maximum bitrate for video calls (default 384 kb/s)")
    rfc2833compensate = fields.Selection(selection=YESNO_VALUES,
        help="""Compensate for pre-1.4 DTMF transmission from another Asterisk machine.
        You must have this turned on or DTMF reception will work improperly.""")
    session_timers = fields.Selection(selection=[(x,x) for x in ('originate', 'accept', 'refuse')],
        help="""Session-Timers feature operates in the following three modes:
        originate : Request and run session-timers always
        accept    : Run session-timers only when requested by other UA
        refuse    : Do not run session timers in any case
        The default mode of operation is 'accept'.""")
    t38pt_usertpsource = fields.Char(size=40,
        help="""Use the source IP address of RTP as the destination IP address for UDPTL packets
        if the nat option is enabled. If a single RTP packet is received Asterisk will know the
        external IP address of the remote device. If port forwarding is done at the client side
        then UDPTL will flow to the remote device.""")
    regexten = fields.Char(size=40,
        help = """When device registers, create this extension in context set with 'regcontext' general option
        By default peer's name is used""")
    sendrpid = fields.Selection(selection=YESNO_VALUES)
    timert1 = fields.Integer(help="""SIP T1 timer. Defaults to 500 ms
        or the measured round-trip time to a peer (qualify=yes).""")
    timerb = fields.Integer(
        help = """Call setup timer. If a provisional response is not received
        in this amount of time, the call will autocongest
        Defaults to 64*timert1""")
    qualifyfreq = fields.Integer(
        help = """How often to check for the host to be up in seconds.
        Set to low value if you use low timeout for NAT of UDP sessions.
        Default: 60""")
    contactpermit = fields.Char(size=95, help = "IP address filters for registrations")
    contactdeny = fields.Char(size=95, help = "IP address filters for registrations")
    contactacl = fields.Char(size=95, help = "IP address filters for registrations")
    usereqphone = fields.Selection(selection=YESNO_VALUES,
        help="If yes, ';user=phone' is added to uri that contains a valid phone number")
    textsupport = fields.Selection(selection=YESNO_VALUES,
        help="Support for ITU-T T.140 realtime text. The default value is 'no'.")
    faxdetect = fields.Selection(selection=YESNO_VALUES)
    buggymwi = fields.Selection(selection=YESNO_VALUES)
    callingpres = fields.Selection(selection=[(x, x) for x in
                ('allowed_not_screened', 'allowed_passed_screen',
                 'allowed_failed_screen', 'allowed',
                 'prohib_not_screened', 'prohib_passed_screen',
                 'prohib_failed_screen', 'prohib')])
    mohinterpret = fields.Char(size=40)
    mohsuggest = fields.Char(size=40)
    parkinglot = fields.Char(size=40,
                             help='Sets the default parking lot for call '
                                  'parking. Parkinglots are configured '
                                  'in features.conf')
    subscribemwi = fields.Selection(selection=YESNO_VALUES,
                                    help='Only send notifications if this '
                                         'phone subscribes for mailbox '
                                         'notification')
    vmexten = fields.Char(size=40,
                          help='dialplan extension to reach mailbox sets the '
                               'Message-Account in the MWI notify message '
                               'defaults to global vmexten which defaults '
                               'to "asterisk')
    autoframing = fields.Selection(YESNO_VALUES,
        help = """Set packetization based on the remote endpoint's (ptime) preferences.
        Defaults to no.""")
    rtpkeepalive = fields.Integer(help="""Integer. Send keepalives in the RTP stream to keep NAT open.
        Default is off - zero.""")
    g726nonstandard = fields.Selection(selection=YESNO_VALUES,
        help = """If the peer negotiates G726-32 audio, use AAL2 packing
        order instead of RFC3551 packing order (this is required
        for Sipura and Grandstream ATAs, among others). This is
        contrary to the RFC3551 specification, the peer _should_
        be negotiating AAL2-G726-32 instead :-(""")
    ignoresdpversion = fields.Selection(selection=YESNO_VALUES,
        help = """By default, Asterisk will honor the session version
        number in SDP packets and will only modify the SDP
        session if the version number changes. This option will
        force asterisk to ignore the SDP session version number
        and treat all SDP data as new data.  This is required
        for devices that send us non standard SDP packets
        (observed with Microsoft OCS). By default this option is off.""")
    allowtransfer = fields.Selection(selection=YESNO_VALUES,
        help = """Diable/Enable SIP transfers.
        The Dial() options 't' and 'T' are not related as to whether SIP transfers are allowed or not.""")
    supportpath = fields.Selection(selection=YESNO_VALUES,
        help = "This activates parsing and handling of Path header as defined in RFC 3327")
    # Status fields
    status = fields.Char(size=32)
    useragent = fields.Char(size=255, string='User agent')
    ipaddr = fields.Char(size=45, string='IP address')
    regport = fields.Integer(string="Port")
    fullcontact = fields.Char(size=80, string='Full contact')
    regexpire = fields.Char(size=32)
    session_expire = fields.Char(size=32)
    regseconds = fields.Char(size=32, help=_('Number of seconds between '
                                             'SIP REGISTER.'))
    regseconds_human = fields.Char(compute='_get_regseconds_human',
                                   string='Last Reg')    


    _sql_constraints = [
        ('name_uniq', 'UNIQUE(name,server)',
             _('Peer name for this server is already used!'))
    ]


    @api.constrains('name')
    def _check_name(self):
        allowed_chars = string.ascii_letters + string.digits + '_-'
        for l in self.name:
            if l not in allowed_chars:
                raise ValidationError(_('Peer name must be only letters, '
                                        'digits, - or _'))

    @api.depends('peer_statuses')
    def _get_peer_status_count(self):
        for rec in self:
            rec.peer_status_count = self.env[
                'asterisk.sip_peer_status'].search_count([
                    ('peer', '=', rec.id)])



    @api.model
    def create(self, vals):
        res = super(SipPeer, self.with_context(
                                    {'on_sip_peer_create': True})).create(vals)
        if res:
            if res.extension:
                res.extension_id = self.env['asterisk.extension'].sudo().create({
                                                'extension_type': 'sip_peer',
                                                'server': res.server.id,
                                                'sip_peer': res.id})
                self.env['asterisk.extension'].sudo().build_conf()
            self.sudo().build_conf()
        return res


    @api.multi
    def write(self, vals):
        if 'extension' in vals:
            for rec in self:
                if vals['extension'] and not rec.extension_id:
                    self.env['asterisk.extension'].sudo().create({
                                                'extension_type': 'sip_peer',
                                                'server': rec.server.id,
                                                'sip_peer': rec.id})
                elif rec.extension_id and not vals['extension']:
                    rec.extension_id.unlink()
                # Commit record changes
                super(SipPeer, rec).write(vals)
        else:
            super(SipPeer, self).write(vals)
        self.sudo().build_conf()
        return True


    @api.multi
    def unlink(self):
        res = super(SipPeer, self).unlink()
        if res:
            self.sudo().build_conf()
            self.env['asterisk.extension'].sudo().build_conf()
        return res


    @api.multi
    def _get_user_list(self):
        for rec in self:
            rec.user_list = ','.join([k.partner.name for k in rec.user])


    @api.depends('extension', 'user.extension')
    @api.multi
    def _get_extension(self):
        for rec in self:
            rec.extension_list = rec.user.extension if rec.user else rec.extension


    @api.onchange('server')
    def reset_server(self):
        self.route_group = False


    def build_conf(self):
        # Build trunks
        def build_peers_conf(records, conf_name):
            # Now create config data
            conf_dict = {}
            for rec in records:
                if not conf_dict.get(rec.server.id):
                    conf_dict[rec.server.id] = ''
                channel_vars = rec.setvar.split(';') if rec.setvar else []
                if rec.peer_type == 'user':
                    channel_vars.append('route_group_id={}'.format(
                                                rec.route_group.id))
                rendered = self.env['ir.qweb'].render(
                                'asterisk_base.asterisk_sip_peer', {
                                'rec': rec,
                                'channel_vars': channel_vars})
                conf_dict[rec.server.id] += '{}'.format(rendered.decode('latin-1'))
            # Create conf files§
            for server_id in conf_dict.keys():
                # First try to get existing conf
                conf = self.env['asterisk.conf'].search(
                                   [('server', '=', server_id),
                                    ('name', '=', conf_name)])
                if not conf:
                    # Create a new one
                    conf = self.env['asterisk.conf'].create(
                                           {'server': server_id,
                                            'name': conf_name})
                # Set conf content
                conf.content = '{}'.format(
                                    remove_empty_lines(conf_dict[server_id]))
                conf.include_from('sip.conf')

        # Clear conf files first
        for c in self.env['asterisk.conf'].search([
                                        ('name', 'like', 'sip_odoo_')]):
            c.content = ''
        # Build conf for different PEER_TYPES
        for pt in PEER_TYPES:
            records = self.env['asterisk.sip_peer'].search(
                                                [('peer_type', '=', pt[0])])
            build_peers_conf(records, 'sip_odoo_{}.conf'.format(pt[0]))


    @api.multi
    def reload(self):
        self.ensure_one()
        self.server.reload(module='chan_sip')


    @api.multi
    def sync_button(self):
        self.ensure_one()
        self.sync(try_offline=True)


    def sync(self, try_offline=False, notify_offline=False):
        self.ensure_one()
        self.build_conf()
        self.server.apply_changes(try_offline=try_offline,
                                  notify_offline=notify_offline)


    @api.multi
    def _get_regseconds_human(self):
        for rec in self:
            if HUMANIZE:
                to_translate = self.env.context.get('lang', 'en_US')
                if to_translate != 'en_US':
                    humanize.i18n.activate(to_translate)
                rec.regseconds_human = humanize.naturaltime(datetime.fromtimestamp(
                    float(rec.regseconds)))  if rec.regseconds else ''
            else:
                rec.regseconds_human = rec.regseconds


