#!/usr/bin/env python3.6
"""
Asterisk Agent is a middlware between Odoo and Asterisk.
It connects to Odoo using XML-RPC and connects to Asterisk using AMI
(Asterisk Management Interface).
"""
import asyncio
import aiohttp
import aiofiles
import base64
import json
import ipaddress
import logging
import os
from pathlib import Path
import re
import socket
import subprocess
import sys
import time
import uuid
import urllib.parse
from panoramisk import Manager
from panoramisk.message import Message as AsteriskMessage
from aiohttp_xmlrpc.client import ServerProxy
if os.getenv('IP_SECURITY_DISABLED') != '1':
    # We must set XTABLES_LIBDIR for iptc
    if not os.getenv('XTABLES_LIBDIR'):
        os.environ['XTABLES_LIBDIR'] = '/usr/lib/xtables'
    import iptc
    from ipsetpy import ipset_list, ipset_create_set, ipset_add_entry
    from ipsetpy import ipset_del_entry, ipset_test_entry, ipset_flush_set
    from ipsetpy.exceptions import IpsetError, IpsetNoRights


logging.basicConfig(level=logging.DEBUG,
                    format='%(asctime)s %(levelname)s %(message)s')
logging.getLogger('asyncio').setLevel(logging.WARNING)
logging.getLogger('panoramisk.manager').setLevel(logging.WARNING)
logging.getLogger('aiohttp_xmlrpc.client').setLevel(logging.WARNING)
logger = logging.getLogger(__name__)

if os.getenv('SENTRY_ENABLED', '0') == '1':
    """
    Sentry can be used in production environment to catch exceptions and report errors.
    """
    import sentry_sdk
    sentry_sdk.init(os.getenv('SENTRY_URL', ''))
    logger.info('Sentry initialized')

# Download and upload only files with the following extensions
CONF_EXT = ['.conf', '.ael', '.lua', '.adsi', '.timers']

loop = asyncio.get_event_loop()

# Asterisk AMI manager client
manager = Manager(loop=loop,
                  host=os.getenv('MANAGER_HOST', 'localhost'),
                  port=int(os.getenv('MANAGER_PORT', '5038')),
                  username=os.getenv('MANAGER_LOGIN', 'odoo'),
                  secret=os.getenv('MANAGER_SECRET', 'odoo'))
manager.loop.set_debug(False)


ORIGINATE_RESPONSE_CODES = {
    '0': 'No such extension / number or bad dial tech ie. name of a SIP trunk'
         'that doesn\'t exist',
    '1': 'No answer',
    '4': 'Answered',
    '5': 'Busy',
    '8': 'Congested or not available (Disconnected Number)'
}

# ipset list member line example: 10.18.0.100 timeout 0 packets 0 bytes 0 comment "Admin added"
re_ipset_entry = re.compile(r'^(\d{1,3}\.\d{1,3}\.\d{1,3}\.\d{1,3}(?:/\d{1,2})?) timeout ([0-9]+) packets ([0-9]+) bytes ([0-9]+) comment "(.+)"$')


class AsteriskAgent(object):
    loop = None
    server_id = None
    odoo_connected = asyncio.Event()
    odoo_disconnected = asyncio.Event()
    server_registered = asyncio.Event()
    manager_connected = asyncio.Event()
    settings_received = asyncio.Event()
    # These are set in connect_odoo method
    odoo_uid = None
    odoo_xmlrpc_url = None
    odoo_db = None
    odoo_login = None
    odoo_password = None
    odoo_execute_q = None
    # Settings
    asterisk_etc_dir = os.getenv('ASTERISK_CONF_DIR', '/etc/asterisk')
    # IP Ban default settings
    ip_security_enabled = False
    ip_ban_seconds = 300
    filter_ports = '5060,4569'


    def __init__(self, *args, **kwargs):
        self.odoo_execute_q = asyncio.Queue(loop=loop)
        self.client_uid = os.getenv('CLIENT_UID', 's{}'.format(
                                                        str(uuid.getnode())))
        logger.info('Starting asterisk_base agent with UID {}'.format(
                                                            self.client_uid))
        self.odoo_host = os.getenv(
                                'ODOO_HOST', 'odoo')
        self.odoo_port = os.getenv(
                                'ODOO_PORT', '8072')
        self.odoo_scheme = os.getenv(
                                'ODOO_SCHEME', 'http')
        self.odoo_xmlrpc_url = '{}://{}:{}'.format(
                            self.odoo_scheme, self.odoo_host, self.odoo_port)
        self.odoo_db = os.getenv('ODOO_DB', 'asterisk_base')
        self.odoo_login = os.getenv('ODOO_LOGIN', 'agent_test')
        self.odoo_password = os.getenv('ODOO_PASSWORD', 'agent_test')
        self.odoo_longpoll_url = urllib.parse.urljoin(self.odoo_xmlrpc_url,
                                                      '/longpolling/poll')
        self.registration_token = os.getenv('ODOO_REGISTRATION_TOKEN')


    async def start(self):
        # Odoo connections
        asyncio.ensure_future(self.odoo_bus_poll())
        asyncio.ensure_future(self.connect_odoo())
        asyncio.ensure_future(self.register_server())
        asyncio.ensure_future(self.odoo_executor())
        asyncio.ensure_future(self.get_settings())
        asyncio.ensure_future(self.iptables_setup())
        # Asterisk connections
        self.register_asterisk_events()
        logger.info('Connecting to Asterisk.')
        while not self.manager_connected.is_set():
            try:
                await manager.connect()
                self.manager_connected.set()
            except Exception as e:
                logger.error('AMI connect error: {}'.format(e))
                while True:
                    await asyncio.sleep(float(
                                os.getenv('MANAGER_RECONNECT_INTERVAL', 5)))
                    if manager._connected:
                        self.manager_connected.set()
                        break
                break



    async def stop(self):
        """
        We have to cancel all pending coroutines for clean exit.
        """
        logger.info('Stopping')
        await super().stop()

    # Subscribe for the following AMI events that come from Asterisk
    def register_asterisk_events(self):
        if os.getenv('AMI_EVENT_AGENT_CALLED', '0') == '1':
            logger.info('Registering for Agent events')
            manager.register_event('AgentCalled', self.on_asterisk_AgentCalled)
        manager.register_event('Cdr', self.on_asterisk_Cdr)
        manager.register_event('DeviceStateChange',
                               self.on_asterisk_DeviceStateChange)
        manager.register_event('FullyBooted', self.on_asterisk_FullyBooted)
        manager.register_event('Hangup', self.on_asterisk_Hangup)
        manager.register_event('InvalidAccountID',
                               self.on_asterisk_InvalidAccountOrPassword)
        manager.register_event('InvalidPassword',
                               self.on_asterisk_InvalidAccountOrPassword)
        manager.register_event('Newchannel', self.on_asterisk_Newchannel)
        manager.register_event('Newstate', self.on_asterisk_Newstate)
        manager.register_event('NewConnectedLine', self.on_asterisk_Newstate)
        manager.register_event('PeerStatus', self.on_asterisk_PeerStatus)
        manager.register_event('Registry', self.on_asterisk_Registry)
        manager.register_event('VarSet', self.on_asterisk_VarSet)
        manager.register_event('UserEvent', self.on_asterisk_UserEvent)


    async def odoo_bus_poll(self):
        # Wait until we finish registration and asterisk connect procedure
        await self.manager_connected.wait()
        await self.server_registered.wait()
        last = 0
        while True:
            try:
                async with aiohttp.ClientSession() as session:
                    channel = 'asterisk_agent/{}'.format(self.client_uid)
                    logger.debug('Starting Odoo bus poll for {}'.format(channel))
                    # First select database
                    db_select_url = '{}://{}:{}/web?db={}'.format(
                                            self.odoo_scheme, self.odoo_host,
                                            self.odoo_port, self.odoo_db)
                    await session.get(db_select_url, ssl=False)
                    # Now after we tried to select database
                    async with session.get(self.odoo_longpoll_url,
                                           ssl=False,
                                           json={'params': {
                                                    'last': last,
                                                    'channels': [channel],
                                                    }}) as resp:
                        data = await resp.json()
                        result = data.get('result', False)
                        if result == []:
                            # Emtpy response from bus, just continue
                            continue
                        elif not result:
                            logger.error('Bus poll bad result: {}'.format(
                                                            await resp.text()))
                        if last == 0:
                            # Ommit queued data
                            for msg in result:
                                if type(msg['message']) != dict:
                                    message = json.loads(msg['message'])
                                else:
                                    message = msg['message']
                                # Print message if it's not too big
                                if len(str(message)) < 1000:
                                    logger.debug(u'Ommit {}'.format(
                                        json.dumps(message, indent=2)))
                                else:
                                    str_msg = str(message)[:1000]
                                    logger.debug(
                                        u'Big message {}: {}...'.format(
                                                message['command'], str_msg))
                                last = msg['id']
                            continue

                        for msg in result:
                            last = msg['id']
                            if type(msg['message']) != dict:
                                message = json.loads(msg['message'])
                            else:
                                message = msg['message']

                            # Print message is it's not too big
                            if len(str(message)) < 1000:
                                logger.debug('Handle {}'.format(json.dumps(
                                                        message, indent=2)))
                            else:
                                str_msg = str(message)[:1000]
                                logger.debug(
                                    u'Handle big message {}: {}...'.format(
                                                message['command'], str_msg))
                            command = message['command']
                            if hasattr(self, 'on_bus_{}'.format(command)):
                                await getattr(
                                    self, 'on_bus_{}'.format(command))(message)
                            else:
                                logger.error(
                                    'Bus handler not found for {}'.format(command))
            except aiohttp.client_exceptions.ServerDisconnectedError as e:
                logger.error('Disconnected from Odoo bus')
                await asyncio.sleep(
                    float(os.getenv('ODOO_RECONNECT_INTERVAL', '1')))
            except Exception as e:
                if 'Cannot connect' in str(e):
                    logger.error(e)
                else:
                    logger.exception(e)
                await asyncio.sleep(
                    float(os.getenv('ODOO_RECONNECT_INTERVAL', '1')))


    async def odoo_executor(self):
        while True:
            try:
                args = await self.odoo_execute_q.get()
                logger.debug('Odoo execute: {}'.format(args))
                await self.odoo_execute(*args)
            except Exception as e:
                logger.exception(e)


    async def odoo_execute(self, model, method, args, kwargs={}):
        await self.odoo_connected.wait()
        try:
            odoo_session = aiohttp.client.ClientSession(connector=aiohttp.TCPConnector(
                                                            loop=loop,
                                                            verify_ssl=False))
            url = urllib.parse.urljoin(self.odoo_xmlrpc_url,
                                       '/xmlrpc/2/object')
            models = ServerProxy(url, loop=loop, client=odoo_session)
            logger.debug('Odoo execute {} on {} @ {} as {}:{}***{}'.format(
                                        method, model, self.odoo_db,
                                        self.odoo_uid, self.odoo_password[:1],
                                        self.odoo_password[-1:]))
            res = await models.execute_kw(
                                        self.odoo_db,
                                        self.odoo_uid,
                                        self.odoo_password,
                                        model,
                                        method,
                                        args,
                                        kwargs)
            return res
        except Exception as e:
            if 'cannot marshal None unless allow_none is enabled' in str(e):
                pass
            else:
                logger.error(
                    'Error on odoo_execute, model {}, '
                    'method {}, args {}'.format(model, method, args))
                logger.exception(e)
        finally:
            await models.close()


    async def bus_send(self, channel, data):
        try:
            odoo_session = aiohttp.client.ClientSession(connector=aiohttp.TCPConnector(
                                                            loop=loop,
                                                            verify_ssl=False))
            common = ServerProxy("{}/xmlrpc/2/common".format(
                                                    self.odoo_xmlrpc_url),
                                 client=odoo_session,
                                 loop=loop)
            uid = await common.authenticate(self.odoo_db,
                                                      self.odoo_login,
                                                      self.odoo_password,
                                                      {})
            models = ServerProxy('{}/xmlrpc/2/object'.format(
                                                        self.odoo_xmlrpc_url),
                                 client=odoo_session,
                                 loop=loop)
            logger.debug('Bus send to {}: {}'.format(channel, json.dumps(
                                                            data, indent=2)))
            await models.execute_kw(self.odoo_db,
                                    uid,
                                    self.odoo_password,
                                    'asterisk.server',
                                    'rpc_bus_send',
                                    [channel, data])
        except Exception as e:
            logger.exception(e)
        finally:
            if 'common' in vars():
                await common.close()
            if 'model' in vars():
                await models.close()



    async def connect_odoo(self):
        # Wait until we finish registration procedure
        await self.server_registered.wait()
        while True:
            try:
                logger.info('Connecting to Odoo at {}'.format(
                                                        self.odoo_xmlrpc_url))
                odoo_session = aiohttp.client.ClientSession(connector=aiohttp.TCPConnector(
                                                            loop=loop,
                                                            verify_ssl=False))
                common = ServerProxy("{}/xmlrpc/2/common".format(
                                                        self.odoo_xmlrpc_url),
                                     client=odoo_session,
                                     loop=loop)
                logger.debug('Odoo authenticate')
                self.odoo_uid = await common.authenticate(self.odoo_db,
                                                          self.odoo_login,
                                                          self.odoo_password,
                                                          {})
                if not self.odoo_uid:
                    logger.error('Cannot authenticate with '
                                 'Odoo using {} / {}'.format(
                                        self.odoo_login, self.odoo_password))
                    os._exit(0)
                logger.debug('Odoo authenticate UID: {}'.format(self.odoo_uid))
                self.odoo_connected.set()
                self.odoo_disconnected.clear()
                # Send the first ping
                channel = 'asterisk_agent/{}'.format(self.client_uid)
                await self.bus_send(channel, {'command': 'ping'})
                await self.odoo_disconnected.wait()
            except Exception as e:
                logger.exception(e)
                await asyncio.sleep(float(
                                os.getenv('ODOO_RECONNECT_TIMEOUT', '1')))

            finally:
                await common.close()


    async def notify_user(self, uid, msg, title=None):
        if not uid:
            logger.debug(u'No uid, will not notify')
            return
        if title:
            msg['Response'] = title
        logger.debug(u'Notify user: {}'.format(json.dumps(msg, indent=2)))
        if msg.get('Success'):
            notify_type = 'notify_info_{}'.format(uid)
        else:
            notify_type = 'notify_warning_{}'.format(uid)
        await self.bus_send(notify_type,
                            {'message': msg.get('Message', ''),
                             'title': msg.get('Response', '')})


    async def register_server(self):
        if not self.registration_token:
            logger.info('No registration token set, omitting registration')
            self.server_registered.set()
            return
        while True:
            try:
                async with aiohttp.ClientSession() as session:
                    # First select database
                    db_select_url = '{}/web?db={}'.format(self.odoo_xmlrpc_url,
                                                          self.odoo_db)
                    await session.get(db_select_url, ssl=False)
                    url = urllib.parse.urljoin(self.odoo_xmlrpc_url,
                                               '/asterisk_base/register_server')
                    logger.info('Registering to {} with UID {}'.format(
                                                            url, self.client_uid))
                    async with session.post(url, ssl=False, json={
                              'token': self.registration_token,
                              'uid': self.client_uid,
                              'hostname': os.getenv('HOSTNAME') or socket.gethostname(),
                              'cli_url': 'ws://{}:{}/websocket/'.format(
                                    os.getenv('HOSTNAME') or socket.gethostname(),
                                    os.getenv('CONSOLE_LISTEN_PORT', '8010')),
                              'login': self.odoo_login,
                              'password': self.odoo_password}) as resp:
                        reply = await resp.json()
                        if 'error' in reply:
                            logger.error('Could not register server: {}'.format(
                                            json.dumps(reply['error'], indent=2)))
                            os._exit(1)
                        elif reply['result'].get('server_id'):
                            self.server_id = reply['result']['server_id']
                            self.ip_security_enabled = reply[
                                            'result']['ip_security_enabled']
                            self.ip_ban_seconds = reply[
                                                    'result']['ip_ban_seconds']
                            self.filter_ports = reply['result']['filter_ports']
                            self.server_registered.set()
                            logger.info('Register status: {}'.format(
                                                    reply['result']['message']))
                            if reply['result'].get('download_all_conf'):
                                logger.debug('Requesting all conf download')
                                self.odoo_connected.wait()
                                await asyncio.sleep(3)
                                await self.odoo_execute(
                                                    'asterisk.server',
                                                    'download_all_conf',
                                                     [self.server_id])
                            if reply['result'].get('upload_all_conf') and \
                                    os.getenv(
                                            'DOWNLOAD_CONF_AT_START') == '1':
                                # Get latests configs from server
                                logger.info('Download all config files on start')
                                await self.on_bus_save_all_conf({
                                                    'server_id': self.server_id})
                                await self.manager_connected.wait()
                                manager.send_action({'Action': 'Reload'})

                return
            except aiohttp.client_exceptions.ClientConnectorError as e:
                logger.error('{}'.format(e))
                await asyncio.sleep(
                    float(os.getenv('ODOO_RECONNECT_INTERVAL', '1')))
                continue
            except Exception as e:
                logger.exception(e)
                await asyncio.sleep(
                    float(os.getenv('ODOO_RECONNECT_INTERVAL', '1')))
                continue


    async def get_settings(self):
        await self.odoo_connected.wait()
        # For future eeds
        self.settings_received.set()


    async def on_bus_ping(self, message):
        if message.get('reply_channel'):
            await self.bus_send(message['reply_channel'], {'status': 'ok'})


    async def on_bus_originate_call(self, msg):
        uid = msg.pop('uid')
        result = {'Response': 'Started', 'Message': 'Call started'}
        # Check if AMI is alive
        if not manager._connected:
            logger.error('AMI not connected')
            await self.notify_user(uid, {
                             'Response': 'Error',
                             'Message': 'Not connected to Asterisk!'})
            return
        # Check if user's peer is reachable
        if not msg['Channel']:
            # Channel for user is not defined
            logger.error('Channel for UID {} not defined!')
            await self.notify_user(uid, {
                             'Response': 'Error',
                             'Message': 'Origination channel is not defined!'})
            return
        if 'SIP/' in msg['Channel'].upper():
            status = await manager.send_action({
                                        'Action': 'SIPshowpeer',
                                        'Peer': msg['Channel'].split('/')[1]})
            if status.Response == 'Error':
                await self.notify_user(uid, {'Message': status.Message},
                                 title=status.Response)
                logger.error(u'Failed originate for {}: {}'.format(
                                                    msg['Channel'],
                                                    status.Message))
                return False
            elif status.Status.lower() not in ['ok', 'unmonitored']:
                logger.info(
                    'Failed originate for {}, peer status is {}'.format(
                                                    msg['Channel'],
                                                    status.Status))
                await self.notify_user(uid, {
                        'Response': 'Error',
                        'Message': '{} status is {}!'.format(
                                msg['Channel'],
                                status.Status.lower())})
                return False
            else:
                logger.debug(u'Peer {} status is {}, originating'.format(
                            msg['Channel'], status.Status))
        # Go-go-go kukuruza!
        channel_id = uuid.uuid4().hex
        other_channel_id = uuid.uuid4().hex
        action = {
            'Action': 'Originate',
            'CallerID': msg.get('CallerID', ''),
            'Variable': msg.get('Variable', ''),
            'Channel':  msg['Channel'],
            'Exten': msg['Exten'],
            'EarlyMedia': 'true',
            'Context': os.getenv('ORIGINATE_CONTEXT', 'odoo-outgoing'),
            'Priority': '1',
            'Timeout': float(os.getenv('ORIGINATE_TIMEOUT', 60)) * 1000,
            'OtherChannelId': other_channel_id,
            'ChannelId': channel_id,
            'Async': 'true',
        }

        res = await manager.send_action(action)
        if isinstance(res, AsteriskMessage):
            # One message received
            status = res
        else:
            status = res[0]
        if status.Response == 'Error':
            await self.notify_user(uid, {'Response': 'Error',
                                         'Message': status.Message})
            logger.info(u'Originate call for {} to {} status: {}'.format(
                                        msg['Channel'], msg['Exten'], status))
            return
        # Call queued, get the response
        result = res[1]  # OriginateResponse
        response = result.Response
        reason = result.Reason
        if response == 'Failure':
            logger.debug('Originate failed')
            await self.notify_user(uid, {
                'Response': 'Error',
                'Message': ORIGINATE_RESPONSE_CODES.get(
                                                    reason, 'Unknown error')})


    async def on_bus_sip_show_registry(self, message):
        result = await(manager.send_action({'Action': 'SIPshowregistry'}))
        ret = []
        for line in result:
            if line.EventList in ['start', 'Complete']:
                continue
            items = dict(line.items())
            # Remove unsued fields
            items.pop('Event')
            items.pop('ActionID')
            items.pop('content')
            ret.append(items)
        logger.debug('SIP registry: {}'.format(json.dumps(ret, indent=2)))
        reply_channel = message.get('reply_channel')
        if reply_channel:
            await self.bus_send(reply_channel, ret)


    async def on_bus_save_conf(self, message):
        name = message['name']
        logger.info('Saving {}'.format(name))
        async with aiofiles.open(
                    os.path.join(self.asterisk_etc_dir, name), 'wb') as file:
            await file.write(message['content'].encode('latin-1'))
            await file.flush()
            if message.get('reload'):
                await self.asterisk_reload(module=message.get('module'))
        await self.update_conf_versions({name: message['version']})
        reply_channel = message.get('reply_channel')
        if reply_channel:
            await self.bus_send(reply_channel, {'status': 'ok'})


    async def delete_conf_versions(self, names):
        versions_file = os.path.join(self.asterisk_etc_dir, 'versions.txt')
        async with aiofiles.open(versions_file, 'r') as file:
            files_dict = json.loads(await file.read())
            for name in names:
                if name in files_dict:
                    files_dict.pop(name)
        async with aiofiles.open(versions_file, 'w') as file:
            await file.write(json.dumps(files_dict, indent=2))



    async def on_bus_delete_conf(self, message):
        names = message['names']
        logger.info('Deleting {}'.format(','.join(names)))
        for name in names:
            try:
                os.unlink(os.path.join(
                    os.getenv('ASTERISK_CONF_DIR',
                                   '/etc/asterisk'),
                    name))
            except FileNotFoundError:
                pass
        await self.delete_conf_versions(names)
        if message.get('reply_channel'):
            await self.bus_send(message['reply_channel'], {'status': 'done'})


    async def get_conf_version(self, name):
        versions_file = os.path.join(self.asterisk_etc_dir, 'versions.txt')
        if not os.path.exists(versions_file):
            return '1'
        async with aiofiles.open(versions_file, 'r') as file:
            files_dict = json.loads(await file.read())
            return files_dict.get(name, '1')


    async def update_conf_versions(self, data_dict):
        versions_file = os.path.join(self.asterisk_etc_dir, 'versions.txt')
        if not os.path.exists(versions_file):
            files_dict = {}
        else:
            async with aiofiles.open(versions_file, 'r') as file:
                files_dict = json.loads(await file.read() or '{}')
        for name, version in data_dict.items():
            files_dict[name] = version
        # Now save the file
        async with aiofiles.open(versions_file, 'w') as file:
            await file.write(json.dumps(files_dict, indent=2))
        #logger.debug('Saved version.txt: {}'.format(
        #                                    json.dumps(files_dict, indent=2)))



    async def on_bus_get_conf(self, message):
        name = message['name']
        reply_channel = message.get('reply_channel')
        logger.info('Get conf {}'.format(name))
        try:
            async with aiofiles.open(
                        os.path.join(
                            os.getenv('ASTERISK_CONF_DIR', '/etc/asterisk'),
                            name), 'rb') as file:
                data = await file.read()
                if reply_channel:
                    await self.bus_send(reply_channel, {
                                'content': data.decode('latin-1'),
                                'version': await self.get_conf_version(name)})
        except FileNotFoundError:
            logger.warning('File not found: {}'.format(name))
            if reply_channel:
                await self.bus_send(reply_channel, {'error': 'File not found!'})



    async def on_bus_get_all_conf(self, message):
        logger.debug('Get all conf')
        result = []
        path = Path(os.getenv('ASTERISK_CONF_DIR', '/etc/asterisk'))
        for file in [
            x for x in path.iterdir() if x.is_file() and x.suffix in CONF_EXT]:
            logger.debug('Getting {}'.format(file.name))
            try:
                async with aiofiles.open(path / file, mode='rb') as f:
                    data = await f.read()
                    result.append({
                        'name': file.name,
                        'data': base64.b64encode(data),
                        'version': await self.get_conf_version(file.name)
                    })
            except Exception as e:
                logger.exception('Error getting {}'.format(file.name))
        # Upload files
        server_id = message['server_id']
        for line in result:
            line.update({'server': server_id})
            await self.odoo_execute('asterisk.conf', 'rpc_upload_conf', [line])
        # Send back some status information
        if message.get('reply_channel'):
            await self.bus_send(message['reply_channel'], {'status': 'done'})


    async def on_bus_save_all_conf(self, message):
        server_id = message['server_id']
        # Check if we should download all conf files, used on startup
        if not message.get('conf_ids'):
            message['conf_ids'] = await self.odoo_execute('asterisk.conf', 'search', [
                                                [('server', '=', server_id)]])
        odoo_session = aiohttp.client.ClientSession(connector=aiohttp.TCPConnector(
                                                            loop=loop,
                                                            verify_ssl=False))
        models = ServerProxy('{}/xmlrpc/2/object'.format(self.odoo_xmlrpc_url),
                             client=odoo_session,
                             loop=loop)
        data = await models.execute_kw(
                        self.odoo_db,
                        self.odoo_uid,
                        self.odoo_password,
                        'asterisk.conf',
                        'read',
                        [message['conf_ids']],
                        {'fields': ['name', 'content', 'version']})
        await models.close()
        for conf in data:
            await self.on_bus_save_conf({'name': conf['name'],
                                         'version': conf['version'],
                                         'content': conf['content']})
        if message.get('reply_channel'):
            await self.bus_send(message['reply_channel'], {'status': 'ok'})


    async def on_bus_save_voice_prompt(self, message):
        sounds_dir = os.getenv('ASTERISK_SOUNDS_DIR',
                                    '/var/lib/asterisk/sounds/')
        odoo_sounds_dir = os.path.join(sounds_dir, 'odoo')
        # Create odoo sounds dir if not set
        if not os.path.isdir(odoo_sounds_dir):
            os.mkdir(odoo_sounds_dir)
        # Save file
        async with aiofiles.open(
                            os.path.join(odoo_sounds_dir, message['name']),
                            'wb') as file:
            await file.write(base64.b64decode(message['data']))
            await file.flush()
        if message.get('reply_channel'):
            await self.bus_send(message['reply_channel'], {'status': 'ok'})


    async def asterisk_reload(self, module=None):
        if not module:
            logger.info('Reload')
            await manager.send_action({'Action': 'Reload'})
        else:
            logger.info('Reload module {}'.format(module))
            await manager.send_action({'Action': 'Reload', 'Module': module})


    async def on_bus_asterisk_reload(self, message):
        module = message.get('module')
        await self.asterisk_reload(module)
        if message.get('reply_channel'):
            await self.bus_send(message['reply_channel'], {'status': 'ok'})


    async def on_asterisk_FullyBooted(self, manager, event):
        logger.info('FullyBooted')


    async def on_asterisk_AgentCalled(self, manager, event):
        logger.debug('Agent Called: {}'.format(json.dumps(
                                                    dict(event.items()),
                                                    indent=2)))
        msg = {
            'Interface': event['Interface'],
            'MemberName': event['MemberName'],
            'Queue': event['Queue'],
            'CallerIDNum': event['CallerIDNum'],
        }
        await self.bus_send('asterisk_agent_called', msg)


    async def on_asterisk_Newchannel(self, manager, event):
        logger.debug('Asterisk event Newchannel: {}'.format(json.dumps(
                                            dict(event.items()), indent=2)))
        self.odoo_execute_q.put_nowait(('asterisk.channel', 'new_channel',
                                [dict(event.items())]))


    async def on_asterisk_Newstate(self, manager, event):
        logger.debug('Asterisk event Newstate: {}'.format(json.dumps(
                                            dict(event.items()), indent=2)))
        self.odoo_execute_q.put_nowait(('asterisk.channel', 'update_channel_state',
                                [dict(event.items())]))


    async def on_asterisk_Hangup(self, manager, event):
        logger.debug('Asterisk event Hangup: {}'.format(json.dumps(
                                            dict(event.items()), indent=2)))
        self.odoo_execute_q.put_nowait(('asterisk.channel', 'hangup_channel',
                                [dict(event.items())]))


    async def on_asterisk_UserEvent(self, manager, event):
        logger.debug('Asterisk UserEvent: {}'.format(json.dumps(
                                            dict(event.items()), indent=2)))
        # Find event handler
        method_name = 'on_asterisk_UserEvent_{}'.format(event['UserEvent'])
        logger.debug('Finding {}'.format(method_name))
        if hasattr(self, method_name):
            logger.debug('Calling UserEvent {}'.format(event['UserEvent']))
            await getattr(self, method_name)(manager, event)
        else:
            logger.debug('Ignoring UserEvent {}'.format(event['UserEvent']))


    async def on_asterisk_VarSet(self, manager, event):
         # QoS of CDR
        if event.Variable == 'RTPAUDIOQOS':
            value = event.Value
            pairs = [k for k in value.split(';') if k]
            values = {}
            for pairs in pairs:
                k,v = pairs.split('=')
                values.update({k: v})
            values.update({
                'uniqueid': event.Uniqueid,
                'linkedid': event.Linkedid,
            })
            logger.debug('QoS update: \n{}'.format(json.dumps(
                values, indent=4)))
            loop.call_later(1,
                            self.odoo_execute_q.put_nowait, ('asterisk.cdr',
                                                  'update_qos', [values]))


    async def on_asterisk_PeerStatus(self, manager, event):
        logger.debug('Peer: {}, Address: {}, Status: {}'.format(
            event.Peer, event.Address, event.PeerStatus))
        if event.ChannelType == 'SIP':
            # We only care about SIP registrations
            items = dict(event.items())
            if items['PeerStatus'] in ['Registered', 'Reachable']:
                # Get additional info
                sip_show_peer = await manager.send_action({
                    'Action': 'SIPshowpeer',
                    'Peer': items['Peer'].split('/')[1]
                })
                items['PeerAddress'] = sip_show_peer['Address-IP']
                items['PeerAddressPort'] = sip_show_peer['Address-Port']
                items['UserAgent'] = sip_show_peer['SIP-Useragent']
                items['Status'] = sip_show_peer['Status']
                items['RegContact'] = sip_show_peer['Reg-Contact']
                items['RegExpire'] = sip_show_peer['RegExpire']
                items['SipSessExpires'] = sip_show_peer['SIP-Sess-Expires']
                items['Timestamp'] = time.time()
            self.odoo_execute_q.put_nowait(('asterisk.sip_peer_status',
                                            'update_status', [items]))


    async def on_asterisk_DeviceStateChange(self, manager, event):
        logger.debug('Asterisk DeviceStateChange: {}'.format(json.dumps(
                                            dict(event.items()), indent=2)))


    async def on_asterisk_Registry(self, manager, event):
        logger.debug('Asterisk Registry: {}'.format(json.dumps(
                                            dict(event.items()), indent=2)))
        self.odoo_execute_q.put_nowait(('asterisk.sip_peer_registry',
                                        'update_registry', [dict(event.items())]))


    async def on_asterisk_Cdr(self, manager, event):
        logger.debug('Asterisk event Cdr: {}'.format(json.dumps(
                                            dict(event.items()), indent=2)))
        self.odoo_execute_q.put_nowait(('asterisk.cdr', 'create', [{
            'accountcode': event.AccountCode,
            'src': event.Source,
            'dst': event.Destination,
            'dcontext': event.DestinationContext,
            'clid': event.CallerID,
            'channel': event.Channel,
            'dstchannel': event.DestinationChannel,
            'lastapp': event.LastApplication,
            'lastdata': event.LastData,
            'started': event.StartTime or False,
            'answered': event.AnswerTime or False,
            'ended': event.EndTime or False,
            'duration': event.Duration,
            'billsec': event.BillableSeconds,
            'disposition': event.Disposition,
            'amaflags': event.AMAFlags,
            'uniqueid': event.UniqueID,
            'userfield': event.UserField,
            'server': self.server_id,
        }]))
        if event.Disposition != 'ANSWERED':
            logger.debug('Not sending call record, not answered')
            # Cleanup recording file
            file_path = os.path.join(
                os.getenv('MONITOR_DIR', '/var/spool/asterisk/monitor'),
                '{}.wav'.format(event.Uniqueid))
            if os.path.exists(file_path):
                logger.debug('Removing stale {}'.format(file_path))
                os.unlink(file_path)
            return
        # Upload recording
        if os.getenv('REC_UPLOAD_DISABLED') == '1':
            logger.debug('Recording upload is disabled')
            return
        upload_delay = float(os.getenv('REC_UPLOAD_DELAY', '5'))
        logger.debug('Going to send call recording in {} seconds'.format(
                                                                upload_delay))
        await asyncio.sleep(upload_delay)
        file_path = os.path.join(
                    os.getenv('MONITOR_DIR', '/var/spool/asterisk/monitor'),
                    '{}.wav'.format(event.Uniqueid))
        try:
            async with aiofiles.open(file_path, mode='rb') as file:
                logger.debug('Found call recording for {}'.format
                                                            (event.Uniqueid))
                rec_data = await file.read()
                result = await self.odoo_execute(
                                'asterisk.cdr',
                                'save_call_recording',
                                [{'uniqueid': event.Uniqueid,
                                  'data': base64.b64encode(rec_data).decode()}])
                if not result:
                    logger.error(
                        'Odoo did not save the recording for {}'.format(
                                                            event.Uniqueid))
                    if os.getenv('REC_KEEP_FAILED') != '1':
                        logger.debug('Deleting recording')
                        os.unlink(file_path)
                    else:
                        logger.debug('Keeping recording')
                else:
                    if os.getenv('REC_KEEP_AFTER_UPLOAD') != '1':
                        logger.debug('Call recording saved, deleting file')
                        os.unlink(file_path)
        except FileNotFoundError:
            logger.debug(
                'File recording not found for callid {}'.format(event.Uniqueid))

    @staticmethod
    async def ip_address_get(self):
        url = "https://ident.me"
        async with aiohttp.ClientSession() as session:
            async with session.get(url) as response:
                return await response.text()

###############################################################################
#  IP Security features
###############################################################################

    async def on_asterisk_InvalidAccountOrPassword(self, manager, event):
        # Two events InvalidAccountID & InvalidPassword in one method.
        # logger.debug(f'InvalidAccountOrPassword event: {event}')
        reason = event.Event
        account = event.AccountID
        address = event.RemoteAddress
        service = event.Service
        address_parts = address.split('/')
        logger.info(
            f'InvalidAccountOrPassword account {service}/{account}, '
            f'address {address}')
        if os.getenv('IP_SECURITY_DISABLED') == '1' or not self.ip_security_enabled:
            logger.debug('Ignoring InvalidAccountOrPassword as security is disabled')
            return
        # Check format RemoteAddress='IPV4/UDP/10.18.0.1/35060'
        if len(address_parts) != 4:
            logger.error(f'Security event parse address error: {event}')
        try:
            ip = address_parts[2]
            # Check if this address is not in white list
            if ipset_test_entry('whitelist', ip):
                logger.warning(f'{service} {account} {reason} - whitelisted (no ban)')
            else:
                logger.warning(f'{service} {account} {reason} - banned in blacklist')
                subprocess.check_output(
                    f'ipset add blacklist {ip} --exist --comment "{service} {account} {reason}"',
                    shell=True)
        except subprocess.CalledProcessError as e:
            logger.error(f'ipset add error: {e}')


    async def on_bus_ip_security_get_banned(self, message):
        if os.getenv('IP_SECURITY_DISABLED') == '1' or not self.ip_security_enabled:
            logger.debug('Ignoring ip_security_get_banned as security is disabled')
            return
        result = []
        data = ipset_list('blacklist')
        lines = data.split('\n')
        for line in lines:
            # Try IP style
            found = re_ipset_entry.search(line)
            if found:
                address, timeout, packets, bytes, comment = found.group(1), \
                    found.group(2), found.group(3), found.group(4), found.group(5)
                result.append({
                    'address': found.group(1),
                    'timeout': found.group(2),
                    'packets': found.group(3),
                    'bytes': found.group(4),
                    'comment': found.group(5)
                })
        logger.debug('Banned entries: {}'.format(json.dumps(
                ['{}: {}'.format(k['address'], k['comment']) for k in result],
                indent=2)))
        if message.get('reply_channel'):
           await  self.bus_send(message['reply_channel'], {'entries': result})


    async def on_bus_ip_security_remove_banned(self, message):
        if os.getenv('IP_SECURITY_DISABLED') == '1' or not self.ip_security_enabled:
            logger.debug('Ignoring ip_security_remove_banned as security is disabled')
            return
        for entry in message['entries']:
            ipset_del_entry('blacklist', entry, exist=True)


    async def on_bus_update_access_rules(self, message):
        if os.getenv('IP_SECURITY_DISABLED') == '1' or not self.ip_security_enabled:
            logger.debug('Ignoring update_access_rules as security is disabled')
            return
        # Destroy current sets
        ipset_flush_set('whitelist')
        ipset_flush_set('blacklist')
        # Add new rules
        rules = await self.odoo_execute('asterisk.access_list',
                                        'search_read',
                                        [[['server', '=', self.server_id]]],
                                        {'fields': ['address', 'netmask',
                                                    'address_type',
                                                    'access_type']})
        for rule in rules:
            try:
                ip_netmask = rule['address'] if rule['address_type'] == 'ip' else \
                    '{}/{}'.format(rule['address'],
                                   str(ipaddress.IPv4Network(rule['address'] +
                                        '/' + rule['netmask'])).split('/')[1])
            except (ipaddress.NetmaskValueError, ipaddress.AddressValueError) as e:
                # TODO: On Odoo 11 and 12 do api.constrains for fields
                logger.error('Cannot convert netmask {} for address: {}'.format(
                    rule['netmask'], rule['address']))
                continue
            if rule['access_type'] == 'deny':
                logger.info('Adding {} to blacklist ipset'.format(ip_netmask))
                try:
                    subprocess.check_output(f'ipset add blacklist {ip_netmask} '
                                            '--exist '
                                            '--timeout 0 '
                                            '--comment "Admin added"', shell=True)
                except subprocess.CalledProcessError as e:
                    logger.error(f'ipset add error {e}')
            elif rule['access_type'] == 'allow':
                logger.info('Adding {} to whitelist ipset'.format(ip_netmask))
                ipset_add_entry('whitelist', ip_netmask, exist=True)


    async def iptables_setup(self):
        if os.getenv('IP_SECURITY_DISABLED') == '1':
            logger.info('IP security for agent is disabled')
            return
        # Wait for settings to come form Odoo
        await self.server_registered.wait()
        # Check server setting
        if not self.ip_security_enabled:
            logger.info('IP security for server is disabled')
            return
        # Go!
        logger.info('Enabling IP security')
        astbase_rules = {}
        for port in self.filter_ports.split(','):
            port = str(int(port))  # Check for correct int value
            astbase_rules.update({
                f'4_asterisk_base_wl_{port}_udp': {
                    'protocol': 'udp',
                    'target': 'ACCEPT',
                    'match_dport': port,
                    'match_set': ['whitelist', 'src']
                },
                f'3_asterisk_base_wl_{port}_tcp': {
                    'protocol': 'tcp',
                    'target': 'ACCEPT',
                    'match_dport': port,
                    'match_set': ['whitelist', 'src']
                },
                f'2_asterisk_base_bl_{port}_udp': {
                    'protocol': 'udp',
                    'target': 'DROP',
                    'match_dport': port,
                    'match_set': ['blacklist', 'src']
                },
                f'1_asterisk_base_bl_{port}_tcp': {
                    'protocol': 'tcp',
                    'target': 'DROP',
                    'match_dport': port,
                    'match_set': ['blacklist', 'src']
                }
            })

        def check_ipsets():
            rules_comments = astbase_rules.keys()
            for rule in rules_comments:
                set_name = astbase_rules[rule]['match_set'][0]
                if set_name not in ipset_list():
                    logger.debug('Creating ipset {}'.format(set_name))
                    if set_name == 'blacklist':
                        # Create a set with timeout
                        try:
                            # ipset_create_set does not accept required params
                            subprocess.check_output('ipset create blacklist '
                                                    'hash:net counters comment '
                                                    '--timeout {} '.format(
                                                        self.ip_ban_seconds),
                                                    shell=True)
                        except subprocess.CalledProcessError as e:
                            logger.error(f'ipset create error: {e}')
                    else:
                        # Create a set without timeout
                        ipset_create_set(set_name, 'hash:net')


        def clean_iptables_rules():
            table = iptc.Table(iptc.Table.FILTER)
            input_chain = iptc.Chain(table, 'INPUT')

            def get_astbase_rule():
                rules_comments = astbase_rules.keys()
                # Clear existing rules as we need to follow the order
                for rule in input_chain.rules:
                    for m in rule.matches:
                        if m.name == 'comment' and m.parameters.get(
                                                    m.name) in rules_comments:
                            return rule, m
                return None, None

            while True:
                rule, match = get_astbase_rule()
                if rule:
                    logger.debug('Clearing iptables rule {}'.format(
                                                match.parameters[match.name]))
                    input_chain.delete_rule(rule)
                else:
                    # All cleared
                    break

        def create_iptables_rules():
            table = iptc.Table(iptc.Table.FILTER)
            chain = iptc.Chain(table, 'INPUT')
            # Rule comments as keys
            keys = list(astbase_rules.keys())
            # Sort rules
            keys.sort()
            for key in keys:
                rule = iptc.Rule()
                rule.protocol = astbase_rules[key]['protocol']
                rule.create_target(astbase_rules[key]['target'])
                m1 = rule.create_match(astbase_rules[key]['protocol'])
                m1.dport = astbase_rules[key]['match_dport']
                m2 = rule.create_match('set')
                m2.match_set = astbase_rules[key]['match_set']
                m3 = rule.create_match('comment')
                m3.comment = key
                chain.insert_rule(rule)

        # Setup iptables and ipset rules
        try:
            check_ipsets()
            clean_iptables_rules()
            create_iptables_rules()
            # Download rules
            rules = await self.on_bus_update_access_rules({})
        except (IpsetError, IpsetNoRights) as e:
            logger.error('Disabling security due to setup error {}'.format(e))


if __name__ == '__main__':
    agent = AsteriskAgent(loop=loop)
    loop.create_task(agent.start())
    try:
        loop.run_forever()
    finally:
        logger.info('Stopped')
