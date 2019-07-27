from datetime import datetime, timedelta
import logging
from odoo import models, fields, api, _
from odoo import sql_db
import requests
from urllib.parse import urljoin
try:
    import humanize
    HUMANIZE = True
except ImportError:
    HUMANIZE = False

logger = logging.getLogger(__name__)

ASTERISK_ROLE = 'asterisk' # This PostgreSQL role is used to grant access to CDR table

DISPOSITION_TYPES = (
    ('NO ANSWER', 'No answer'),
    ('FAILED', 'Failed'),
    ('BUSY', 'Busy'),
    ('ANSWERED', 'Answered'),
    ('CONGESTION', 'Congestion'),
)


class Cdr(models.Model):
    _name = 'asterisk.cdr'
    _description = 'Call Detail Record'
    _order = 'started desc'
    _rec_name = 'uniqueid'

    server = fields.Many2one('asterisk.server')
    accountcode = fields.Char(size=20, string='Account code', index=True)
    src = fields.Char(size=80, string='Src', index=True)
    dst = fields.Char(size=80, string='Dst', index=True)
    dcontext = fields.Char(size=80, string='Dcontext')
    clid = fields.Char(size=80, string='Clid', index=True)
    channel = fields.Char(size=80, string='Channel', index=True)
    dstchannel = fields.Char(size=80, string='Dst channel', index=True)
    lastapp = fields.Char(size=80, string='Last app')
    lastdata = fields.Char(size=80, string='Last data')
    started = fields.Datetime(index=True, oldname='start')
    answered = fields.Datetime(index=True, oldname='answer')
    ended = fields.Datetime(index=True, oldname='end')
    duration = fields.Integer(string='Duration', index=True)
    billsec = fields.Integer(string='Billsec', index=True)
    disposition = fields.Char(size=45, string='Disposition', index=True)
    amaflags = fields.Char(size=20, string='AMA flags')
    userfield = fields.Char(size=255, string='Userfield')
    uniqueid = fields.Char(size=150, string='Uniqueid', index=True)
    peeraccount = fields.Char(size=80, string='Peer account', index=True)
    linkedid = fields.Char(size=150, string='Linked id')
    sequence = fields.Integer(string='Sequence')
    recording_filename = fields.Char()
    recording_data = fields.Binary()
    recording_widget = fields.Char(compute='_get_recording_widget')
    # QoS
    ssrc = fields.Char(string='Our SSRC')
    themssrc = fields.Char(string='Other SSRC')
    lp = fields.Integer(string='Local Lost Packets')
    rlp = fields.Integer(string='Remote Lost Packets')
    rxjitter = fields.Float(string='RX Jitter')
    txjitter = fields.Float(string='TX Jitter')
    rxcount = fields.Integer(string='RX Count')
    txcount = fields.Integer(string='TX Count')
    rtt = fields.Float(string='Round Trip Time')
    # CEL related fields
    cel_count = fields.Integer(compute='_get_cel_count')
    cels = fields.One2many(comodel_name='asterisk.cel',
                           inverse_name='cdr')


    @api.multi
    def _get_cel_count(self):
        for rec in self:
            rec.cel_count = self.env['asterisk.cel'].search_count([
                ('cdr', '=', rec.id)])



    @api.multi
    def _get_recording_widget(self):
        for rec in self:
            rec.recording_widget = '<audio id="sound_file" preload="auto" ' \
                    'controls="controls"> ' \
                    '<source src="/web/content?model=asterisk.cdr&' \
                    'id={}&filename={}&field=recording_data&' \
                    'filename_field=recording_filename&download=True" ' \
                    'type="audio/wav"/>'.format(rec.id, rec.recording_filename)


    @api.model
    def update_qos(self, values):
        if type(values) == list:
            values = values[0]
        uniqueid = values.get('uniqueid')
        linkedid = values.get('linkedid')
        # TODO Probably we need to optimize db query on millions of records.
        cdrs = self.env['asterisk.cdr'].search([
            #('ended', '>', (datetime.now() - timedelta(seconds=120)).strftime(
            #    '%Y-%m-%d %H:%M:%S')
            #),
            ('uniqueid', '=', uniqueid),
            #('linkedid', '=', linkedid),
        ])
        if not cdrs:
            logger.warning('Omitting QoS, CDR not found, uniqueid {}!'.format(
                uniqueid))
            return False
        else:
            logger.debug('Found CDR for QoS.')
            cdr = cdrs[0]
            cdr.write({
                 'ssrc': values.get('ssrc'),
                 'themssrc': values.get('themssrc'),
                 'lp': int(values.get('lp')),
                 'rlp': int(values.get('rlp')),
                 'rxjitter': float(values.get('rxjitter')),
                 'txjitter': float(values.get('txjitter')),
                 'rxcount': int(values.get('rxcount')),
                 'txcount': int(values.get('txcount')),
                 'rtt': float(values.get('rtt'))
            })
            return True


    @api.model
    def save_call_recording(self, values):
        if type(values) == list:
            values = values[0]
        call_id = values['uniqueid']
        file_data = values['data']
        logger.debug('save_call_recording for callid {}.'.format(call_id))
        rec = self.env['asterisk.cdr'].search([('uniqueid', '=', call_id)],
                                              limit=1)
        if not rec:
            # Try to find linkedid
            rec = self.env['asterisk.cdr'].search([('linkedid', '=', call_id)],
                                                  limit=1)
            if not rec:
                logger.warning(
                    'cdr for recording not found, uniquid: {}'.format(call_id))
                return False
        logger.debug('Found CDR for id {}.'.format(call_id))
        rec.write({
            'recording_filename': '{}.wav'.format(call_id),
            'recording_data': file_data,
        })
        return True
