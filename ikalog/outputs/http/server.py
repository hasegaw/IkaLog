#!/usr/bin/env python3
# -*- coding: utf-8 -*-
#
#  IkaLog
#  ======
#  Copyright (C) 2015 Takeshi HASEGAWA
#
#  Licensed under the Apache License, Version 2.0 (the "License");
#  you may not use this file except in compliance with the License.
#  You may obtain a copy of the License at
#
#      http://www.apache.org/licenses/LICENSE-2.0
#
#  Unless required by applicable law or agreed to in writing, software
#  distributed under the License is distributed on an "AS IS" BASIS,
#  WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
#  See the License for the specific language governing permissions and
#  limitations under the License.
#

from http.server import HTTPServer, BaseHTTPRequestHandler
from socketserver import ThreadingMixIn
import json
import threading
import traceback

from ikalog.utils import *
from .preview import PreviewRequestHandler

def _get_type_name(var):
    return type(var).__name__


class APIServer(object):

    def _view_game(self, request_handler, payload):
        request_handler.send_response(200)
        request_handler.send_header(
            'Content-type', 'text/html; charset=UTF-8')
        request_handler.end_headers()
        with open(IkaUtils.get_path('tools', 'view.html')) as f:
            data = f.read()
            request_handler.wfile.write(bytearray(data, 'utf-8'))

    def _graph_game(self, request_handler, payload):
        request_handler.send_response(200)
        request_handler.send_header(
            'Content-type', 'text/html; charset=UTF-8')
        request_handler.end_headers()
        with open(IkaUtils.get_path('tools', 'graph.html')) as f:
            data = f.read()
            request_handler.wfile.write(bytearray(data, 'utf-8'))

    def _engine_context_game(self, request_handler, payload):
        request_handler.send_response(200)
        request_handler.send_header(
            'Content-type', 'text/plain; charset=UTF-8')
        request_handler.end_headers()
        request_handler.wfile.write(bytearray(
            json.dumps(request_handler.server.ikalog_context['game'],
                       default=_get_type_name),
            'utf-8'))

    def _engine_preview(self, request_handler, payload):
        handler = PreviewRequestHandler(request_handler)

    def _engine_stop(self, request_handler, payload):
        request_handler.server.ikalog_context['engine']['engine'].stop()

    def process_request(self, request_handler, path, payload):
        handler = {
            '/view': self._view_game,
            '/graph': self._graph_game,
            '/api/v1/engine/context/game': self._engine_context_game,
            '/api/v1/engine/preview': self._engine_preview,
            '/api/v1/engine/stop': self._engine_stop,
        }.get(path, None)

        if handler is None:
            return {'status': 'error', 'description': 'Invalid API Path %s' % path}

        try:
            response_payload = handler(request_handler, payload)
        except:
            return {'status': 'error', 'description': 'Exception', 'detail': traceback.format_exc()}

        return response_payload


class HTTPRequestHandler(BaseHTTPRequestHandler):

    def _send_response_json(self, response):
        body = json.dumps(response)

        self.send_response(200)
        self.send_header('Content-type', 'text/html; charset=utf-8')
        self.send_header('Pragma', 'no-cache')
        self.send_header('Content-length', len(body))
        self.end_headers()
        self.wfile.write(bytearray(body, 'utf-8'))

    def do_GET(self):
        response = self.api_server.process_request(
            self, self.path, {})

    def do_POST(self):
        length = int(self.headers.get('content-length'))
        data = self.rfile.read(length)

        try:
            payload = json.loads(data.decode('utf-8'))
        except:
            payload = None

        if not isinstance(payload, dict):
            try:
                payload = umsgpack.unpackb(data)
            except:
                payload = None

        if isinstance(payload, dict):
            # FIXME: Exception handling
            response = self.api_server.process_request(
                self, self.path, payload)

        else:
            IkaUtils.dprint('%s: Invalid REST API Request' % self)
            print(payload, data)
            response = {'error': 'Invalid request'}

        if response is not None:
            self._send_response_json(response)

        if hasattr(self, 'callback_func'):
            self.callback_func(self.path, payload, response)

    def __init__(self, *args, **kwargs):
        self.api_server = APIServer()
        super(HTTPRequestHandler, self).__init__(*args, **kwargs)


class ThreadedHTTPServer(ThreadingMixIn, HTTPServer):
    """Handle requests in a separate thread."""

    # daemon_threads = False  (default)
    # The process doesn't exit until all of the HTTP requests are processed.


class RESTAPIServer(object):

    def __init__(self, enabled=False, bind_addr='127.0.0.1', port=8888):
        self._bind_addr = bind_addr
        self._port = port
        self._listeners = []

        self._worker_thread = None

    def initialize_server(self, context):
        if self._worker_thread is not None:
            if self._worker_thread.is_alive():
                IkaUtils.dprint(
                    '%s: Waiting for shutdown of server thread' % self)
                self.shutdown_server()

            # XXX
            while self._worker_thread.is_alive():
                time.sleep(2)

            IkaUtils.dprint('%s: server is shut down.' % self)

        self._worker_thread = \
            threading.Thread(target=self._worker_func, args=(self, context))
        self._worker_thread.daemon = True
        self._worker_thread.start()

    def _worker_func(self, self2, context):
        IkaUtils.dprint('%s: serving at %s:%s' %
                        (self, self._bind_addr, self._port))
        httpd = ThreadedHTTPServer(
            (self._bind_addr, self._port), HTTPRequestHandler)
        httpd.ikalog_context = context
        httpd.parent = self
        httpd.serve_forever()
        IkaUtils.dprint('%s: finished serving' % self)

    def on_enable(self, context):
        self.initialize_server(context)

    def on_uncaught_event(self, event_name, context, params=None):
        for listener in self._listeners:
            listener.on_event(event_name, context, params)

if __name__ == "__main__":
    host = 'localhost'
    port = 8000
    httpd = HTTPServer((host, port), HTTPRequestHandler)
    print('serving at port', port)
    httpd.serve_forever()
