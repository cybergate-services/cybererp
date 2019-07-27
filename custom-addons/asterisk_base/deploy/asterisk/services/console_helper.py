#!/usr/bin/env python3
import logging
import os
import ssl
import tornado.web
from tornado.ioloop import IOLoop
from terminado import TermSocket, SingleTermManager
from tornado.web import HTTPError
from tornado.httpserver import HTTPServer

logging.basicConfig(level=logging.DEBUG)
_logger = logging.getLogger(__name__)

ASTERISK = os.environ.get('ASTERISK_BINARY', '/usr/sbin/asterisk')
ASTERISK_ARGS = '-cvvvr'
SSL_ENABLED = False
LISTEN_ADDRESS = os.environ.get('CONSOLE_LISTEN_ADDRESS', '0.0.0.0')
FROM_NGINX = os.environ.get('CONSOLE_FROM_NGINX')
LISTEN_PORT = int(os.environ.get('CONSOLE_LISTEN_PORT', '8010'))


class MyTermSocket(TermSocket):

    def check_origin(self, origin):
        return True

    def get(self, *args, **kwargs):
        if FROM_NGINX != '0':
            # Check
            from_nginx = self.request.query_arguments.get('from_nginx')
            if not from_nginx or from_nginx[0].decode() != FROM_NGINX:
                raise HTTPError(403)
        return super(TermSocket, self).get(*args, **kwargs)


if __name__ == '__main__':
    term_manager = SingleTermManager(shell_command=['sudo', ASTERISK, ASTERISK_ARGS])
    handlers = [
                (r'/websocket/', MyTermSocket, {'term_manager': term_manager}),
               ]

    # Create SSL context
    if SSL_ENABLED:
        #ssl_ctx = ssl.create_default_context()
        ssl_ctx = ssl.SSLContext()
        ssl_ctx.check_hostname = False
        #ssl_ctx.verify_mode = ssl.CERT_NONE
    else:
        ssl_ctx = None

    # Start server
    app = tornado.web.Application(handlers)
    server = HTTPServer(app, ssl_options=ssl_ctx)
    server.listen(LISTEN_PORT, address=LISTEN_ADDRESS)
    IOLoop.current().start()