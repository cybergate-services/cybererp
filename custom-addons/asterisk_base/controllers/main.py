import logging
import random
import os
import shutil
import string
import subprocess
import tempfile
from urllib.parse import urlparse
from odoo import http
from odoo.exceptions import Warning, AccessDenied
from werkzeug.exceptions import Forbidden, NotAcceptable

logger = logging.getLogger(__name__)


class AsteriskBaseController(http.Controller):

    @http.route('/asterisk_base/register_server', type='json', auth='public',
                methods=['POST'])
    def register_server(self):
        data = http.request.jsonrequest
        # Find the user
        try:
            login_id = http.request.env['res.users'].sudo()._login(
                                                http.request.db,
                                                data['login'],
                                                data['password'])
            # No need to prcoess token registration
            login = http.request.env['res.users'].sudo().browse(login_id)
            if not login.asterisk_base_server:
                raise NotAcceptable('No Asterisk server for login!')
            elif login.asterisk_base_server.uid != data['uid']:
                raise NotAcceptable('Server''s UID does not match Agent UID!')
            return {'server_id': login.asterisk_base_server[0].id,
                    'ip_security_enabled': login.asterisk_base_server[0].ip_security_enabled,
                    'ip_ban_seconds': login.asterisk_base_server[0].ip_ban_seconds,
                    'filter_ports':  login.asterisk_base_server[0].filter_ports,
                    'upload_all_conf': True,
                    'message': 'Login found'}

        # No registration yet
        except AccessDenied:
            # Process wirh registration token
            token = data['token']
            registration_token = http.request.env['res.config.settings'].sudo(
                                    )._get_asterisk_param('device_registration_token')
            if registration_token != token:
                logger.error('Registration attempt with non-existent '
                             'token {}'.format(token))
                raise NotAcceptable('Bad registration token')
            # Search for server if it exists
            server = http.request.env['asterisk.server'].sudo().search([
                ('uid', '=', data['uid'])])
            if not server:
                # Check login
                if http.request.env['res.users'].sudo().search(
                                            [('login', '=', data['login'])]):
                    raise Warning('This login is not availale')
                server = http.request.env['asterisk.server'].sudo().create({
                    'name': data['hostname'],
                    'uid': data['uid'],
                    'hostname': data['hostname'],
                    'login_username': data['login'],
                    'login_password': data['password'],
                    'cli_url': data['cli_url'],
                    'state': 'online',
                })
                return {
                    'server_id': server.id,
                    'message': 'Server created',
                    'download_all_conf': True,
                    'ip_security_enabled': server.ip_security_enabled,
                    'ip_ban_seconds': server.ip_ban_seconds,
                    'filter_ports':  server.filter_ports,
                }
            else:
                return {
                    'server_id': server.id,
                    'message': 'Server exists',
                    'ip_security_enabled': server.ip_security_enabled,
                    'ip_ban_seconds': server.ip_ban_seconds,
                    'filter_ports':  server.filter_ports,
                }


    @http.route('/asterisk_base/download/agent', auth='user')
    def download_agent(self):
        # Check permission
        user = http.request.env['res.users'].sudo().browse(http.request.uid)
        if not user.has_group('asterisk_base.group_asterisk_base_admin'):
            raise Forbidden(
                        'Only Asterisk admin can download the agent!')
        try:
            filename = 'asterisk_base_agent.tar.gz'
            temp_dir = tempfile.mkdtemp()
            agent_dir = os.path.join(temp_dir, 'asterisk_base_agent')
            os.mkdir(agent_dir)
            tar_f, tar_path = tempfile.mkstemp()
            current_dir = os.path.dirname(__file__)
            # Copy agent.py
            shutil.copy(
                os.path.join(current_dir, '..', 'deploy', 'asterisk',
                             'services', 'agent.py'), agent_dir)
            # Copy console_helper.py
            shutil.copy(
                os.path.join(current_dir, '..', 'deploy', 'asterisk',
                             'services', 'console_helper.py'), agent_dir)
            # Copy requirements.txt
            shutil.copy(
                os.path.join(current_dir, '..', 'deploy', 'asterisk',
                             'services', 'requirements.txt'), agent_dir)
            # Create and copy start_agent.sh
            agent_start = os.path.join(agent_dir, 'start_agent.sh')
            # Parse url to guess initial values
            host_url = urlparse(http.request.httprequest.host_url)
            # Generate random user and password
            with open(agent_start, 'w') as f:
                f.write('#!/bin/bash\n\n')
                f.write('export ODOO_LOGIN=agent_{}\n'.format(''.join(
                                    random.sample(string.ascii_lowercase, 8))))
                f.write('export ODOO_PASSWORD={}\n'.format(
                    ''.join(random.sample(
                                string.ascii_lowercase + string.digits, 16))))
                f.write('export ODOO_REGISTRATION_TOKEN={}\n'.format(
                    http.request.env['res.config.settings'].sudo()._get_asterisk_param(
                                                'device_registration_token')))
                f.write('export ODOO_DB={}\n'.format(http.request.session.db))
                f.write('export ODOO_HOST={}\n'.format(
                    http.request.env['res.config.settings'].sudo()._get_asterisk_param(
                                                        'agents_hostname')))
                f.write('export ODOO_PORT={}\n'.format(
                    http.request.env['res.config.settings'].sudo()._get_asterisk_param(
                                                        'agents_port')))
                f.write('export ODOO_SCHEME={}\n'.format(
                    http.request.env['res.config.settings'].sudo()._get_asterisk_param(
                                                        'agents_security')))
                f.write('export ODOO_RECONNECT_INTERVAL=1\n')
                f.write('export DEBUG=0\n')
                f.write('export MANAGER_LOGIN=odoo\n')
                f.write('export MANAGER_PASSWORD=odoo\n')
                f.write('export ASTERISK_CONF_DIR=/etc/asterisk\n')
                f.write('export ASTERISK_SOUNDS_DIR=/usr/share/asterisk/sounds/\n')
                f.write('exec python3 agent.py\n\n')
            os.chmod(agent_start, 0o775)
            # Compress and create the archive
            subprocess.call(
                    'tar cfz {} -C {} asterisk_base_agent'.format(
                                            tar_path, temp_dir), shell=True)
            headers, content = [], open(tar_path, 'rb').read()
            headers += [('Content-Type', 'application/octet-stream'),
                        ('X-Content-Type-Options', 'nosniff')]
            headers.append(('Cache-Control', 'max-age=0'))
            headers.append(('Content-Disposition', http.content_disposition(
                                                                    filename)))
            headers.append(('Content-Length', len(content)))
            response = http.request.make_response(content, headers)
            return response
        finally:
            shutil.rmtree(temp_dir)
            os.unlink(tar_path)

