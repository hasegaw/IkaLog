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

from http.server import HTTPServer, SimpleHTTPRequestHandler
from socketserver import ThreadingMixIn
from urllib.parse import urlparse, parse_qs
from collections import ChainMap
import json
import platform
import threading
import traceback
import errno

from ikalog.utils import *
from .preview import PreviewRequestHandler
from ikalog.version import IKALOG_VERSION


def _get_type_name(var):
    return type(var).__name__


def _request_handler2engine(request_handler):
    return request_handler.server.ikalog_context['engine']['engine']


def _get_plugins_list(engine):
    r = {}
    cond = lambda x: hasattr(x, 'get_configuration')
    plugins = filter(cond, engine.output_plugins)
    for plugin in plugins:  # engine.output_plugins:
        if hasattr(plugin, 'plugin_name'):
            plugin_name = plugin.plugin_name
        else:
            plugin_name = plugin.__class__.__name__

        r[plugin_name] = plugin
    return r


class Response(object):

    def __init__(self, *args, **kwargs):
        self.status = 200
        self.content_type = 'application/json'
        self.charset = 'utf-8'
        self.response = {}

    def send(self, request_handler):
        content_binary = self._format()
        if (self.charset is not None):
            content_type = '{}; charset={}'.format(
                self.content_type, self.charset)
        else:
            content_type = self.content_type
        request_handler.send_response(self.status)
        request_handler.send_header('Content-Type', content_type)
        request_handler.send_header('Content-Length', len(content_binary))
        request_handler.send_header('Access-Control-Allow-Origin', '*')
        request_handler.end_headers()
        request_handler.wfile.write(content_binary)

    def _format(self):
        if isinstance(self.response, bytearray):
            return self.response

        if self.content_type != 'application/json':
            return bytearray(self.response, self.charset)

        return bytearray(
            json.dumps(self.response, ensure_ascii=False,
                       default=_get_type_name),
            self.charset
        )


class APIServer(object):

    def _prepare_send_file(self, request_handler, payload, path, content_type):
        response = Response()
        try:
            with open(path, mode='rb') as f:
                response.content_type = content_type
                response.charset = None
                response.response = bytearray(f.read())

        except OSError as e:
            if e.errno == errno.ENOENT:
                response.status = 404
                response.content_type = 'text/plain'
                response.response = 'Not found'
            elif e.errno == errno.EACCES:
                response.status = 403
                response.content_type = 'text/plain'
                response.response = 'Forbidden'
            else:
                response.status = 500
                response.content_type = 'text/plain'
                response.response = 'Server Error'
        except:
            response.status = 500
            response.response = 'Server Error'
        return response

    def _view_game(self, request_handler, payload):
        return self._prepare_send_file(request_handler, payload,
                                       IkaUtils.get_path('tools', 'view.html'), 'text/html')

    def _graph_game(self, request_handler, payload):
        return self._prepare_send_file(request_handler, payload,
                                       IkaUtils.get_path('tools', 'graph.html'), 'text/html')

    def _engine_context_game(self, request_handler, payload):
        response = Response()
        response.response = request_handler.server.ikalog_context['game']
        return response

    def _engine_source(self, request_handler, payload):
        response = Response()
        response.content_type = 'text/plain'
        engine = _request_handler2engine(request_handler)
        file_path = payload.get('file_path')
        if (not file_path) or (not engine.put_source_file(file_path)):
            response.status = 400
            response.response = 'error'
        else:
            response.response = file_path
        return response

    def _engine_preview(self, request_handler, payload):
        handler = PreviewRequestHandler(request_handler)

    def _engine_stop(self, request_handler, payload):
        engine = _request_handler2engine(request_handler)
        engine.stop()

    def _input_devices(self, request_handler, payload):
        cameras = []
        if IkaUtils.isWindows():
            from ikalog.inputs.win.videoinput_wrapper import VideoInputWrapper
            cameras = VideoInputWrapper().get_device_list()

        response = Response()
        response.response = cameras
        return response

    def _screenshot_save(self, request_handler, payload):
        engine = _request_handler2engine(request_handler)
        screenshot_save_func = engine.get_service('screenshot_save')
        context = request_handler.server.ikalog_context
        frame = context['engine']['frame']

        response = Response()
        if screenshot_save_func and screenshot_save_func(frame):
            response.response = {'status': 'ok',
                                 'message': 'Saved a screenshot'}
        else:
            response.response = {'status': 'failed',
                                 'message': 'Failed to save a screenshot'}
        return response

    def _config_get(self, request_handler, payload):
        engine = _request_handler2engine(request_handler)
        plugins = _get_plugins_list(engine)

        config = {}
        for plugin_name in plugins.keys():
            plugin = plugins[plugin_name]
            config[plugin_name] = plugin.get_configuration()

        response = Response()
        response.response = {'status': 'ok', 'configuration': config}
        return response

    def _config_validate(self, request_handler, payload):
        validation_result = []
        payload = dict(payload)
        engine = _request_handler2engine(request_handler)
        plugins = _get_plugins_list(engine)

        new_config = payload.get('configuration', {})
        for plugin_name in new_config.keys():
            if not (plugin_name in plugins):
                validation_result.append({
                    'error': 'PLUGIN_NOT_SUPPORTED',
                    'plugin': plugin_name
                })
                continue

            try:
                conf = new_config[plugin_name]
                plugin.validate_configuration(conf)
            except AssertionError:
                # FIXME: Return more information.
                validation_result.append({
                    'error': 'PLUGIN_CONFIG_INVALID',
                    'plugin': plugin_name,
                })
                IkaUtils.dprint(traceback.format_exc())
            except:
                validation_result.append({
                    'error': 'PLUGIN_CONFIG_INVALID',
                    'plugin': plugin_name,
                    'exception': True,
                })
                IkaUtils.dprint(traceback.format_exc())

        if len(validation_result) > 0:
            # Validation Error
            response = Response()
            response.response = {
                'status': 'error',
                'error': validation_result
            }
            return response

        response = Response()
        response.response = {'status': 'ok'}
        return response

    def _status_get(self, request_handler, payload):
        engine = _request_handler2engine(request_handler)
        plugins = _get_plugins_list(engine)

        status = {
            'status': 'ok',
            'is_windows': IkaUtils.isWindows(),
            'is_osx': IkaUtils.isOSX(),
            'version': IKALOG_VERSION,
            'stopped': engine.is_stopped(),
            'paused': engine.is_paused(),
            'platform_system': platform.system(),
            'platform_machine': platform.machine(),
        }

        response = Response()
        response.response = status
        return response

    def _config_set(self, request_handler, payload):
        validation = self._config_validate(request_handler, payload)
        if validation.response['status'] != 'ok':
            return validation

        new_config = dict(payload)  # new_config = dict(payload)
        engine = _request_handler2engine(request_handler)
        plugins = _get_plugins_list(engine)

        result = []
        for plugin_name in new_config.keys():
            plugin = plugins[plugin_name]
            try:
                conf = new_config[plugin_name]
                plugin.set_configuration(conf)
            except:
                result.append({
                    'error': 'PLUGIN_CONFIG_SET_ERROR',
                    'plugin': plugin_name,
                    'exception': True,
                })
                IkaUtils.dprint(traceback.format_exc())

        if len(result) > 1:
            response = Response()
            response.response = {
                'status': 'error',
                'error': result
            }
            return response

        from ikalog.configuration import write_to_file
        write_to_file(engine, 'ikalog.conf.json')

        return self._config_get(request_handler, payload)

    def _slack_post(self, request_handler, payload):
        response = Response()
        engine = _request_handler2engine(request_handler)
        slack_post = engine.get_service('slack_post')
        if slack_post:
            slack_post(payload['message'])
            response.response = {'status': 'ok', 'message': 'Posted'}
        else:
            response.response = {'status': 'failed', 'message': 'Failed'}
        return response

    def _twitter_post(self, request_handler, payload, screenshot=False):
        engine = _request_handler2engine(request_handler)
        twitter_post = engine.get_service('twitter_post')
        twitter_post_media = engine.get_service('twitter_post_media')

        media = None
        response = Response()
        if screenshot and (twitter_post_media is not None):
            # FIXME: Consider deepcopy.
            context = request_handler.server.ikalog_context
            img = context['engine']['frame']
            media = twitter_post_media(img)

        if twitter_post:
            twitter_post(payload['message'], media=media)
            response.response = {'status': 'ok', 'message': 'Tweeted'}
        else:
            response.response = {'status': 'failed', 'message': 'Failed'}
        return response

    def _twitter_post_screenshot(self, request_handler, payload):
        return self._twitter_post(request_handler, payload, True)

    def _webui_system_info(self, request_handler, payload):
        engine = _request_handler2engine(request_handler)
        twitter_has_preset_key = engine.get_service('twitter_has_preset_key')

        response = Response()
        response.response = {
            "twitter_has_preset_key": twitter_has_preset_key is not None and twitter_has_preset_key(),
            "is_windows": IkaUtils.isWindows(),
            "is_mac": IkaUtils.isOSX(),
            "version": IKALOG_VERSION,
        }
        return response

    def process_request(self, request_handler, path, payload):
        handler = {
            '/view': self._view_game,
            '/graph': self._graph_game,
            '/api/v1/engine/context/game': self._engine_context_game,
            '/api/v1/engine/source': self._engine_source,
            '/api/v1/engine/preview': self._engine_preview,
            '/api/v1/engine/stop': self._engine_stop,
            '/api/v1/input/devices': self._input_devices,
            '/api/v1/webui/system_info': self._webui_system_info,
            '/api/v1/screenshot/save': self._screenshot_save,
            '/api/v1/slack/post': self._slack_post,
            '/api/v1/twitter/post': self._twitter_post,
            '/api/v1/twitter/post_screenshot': self._twitter_post_screenshot,
            '/api/v1/config/get': self._config_get,
            '/api/v1/config/set': self._config_set,
            '/api/v1/config/validate': self._config_validate,
            '/api/v1/status/get': self._status_get,
        }.get(path, None)

        if handler is None:
            response = Response()
            response.status = 404
            response.response = {'status': 'error',
                                 'description': 'Invalid API Path %s' % path}
            return response

        response_payload = handler(request_handler, payload)
        return response_payload


class HTTPRequestHandler(SimpleHTTPRequestHandler):

    def _send_response_json(self, response, status=200):
        resp = Response()
        resp.status = status
        resp.response = response
        resp.send(self)

    def _parse_path(self, path):
        parsed = urlparse(path)
        query = parse_qs(parsed.query)
        return (parsed.path, query)

    def translate_path(self, path):
        assert path.startswith('/')
        path = 'data/wui/html/%s' % path
        return super(HTTPRequestHandler, self).translate_path(path)

    def do_GET(self):
        (path, query) = self._parse_path(self.path)

        if not path.startswith('/api/'):
            super(HTTPRequestHandler, self).do_GET()
            return

        response = self.api_server.process_request(
            self, path, query)

        if response is not None:
            if isinstance(response, Response):
                response.send(self)
            else:
                self._send_response_json(response)

    def do_POST(self):
        (path, query) = self._parse_path(self.path)

        length = int(self.headers.get('content-length'))
        data = self.rfile.read(length)

        try:
            payload = json.loads(data.decode('utf-8'))
        except json.decoder.JSONDecodeError:
            self.dprint(traceback.format_exc())
            response = {'status': 'error', 'message': 'JSON Decode Error'}
            self._send_response_json(response)
            return False

        if not isinstance(payload, dict):
            try:
                payload = umsgpack.unpackb(data)
            except:
                payload = {}

        if isinstance(payload, dict):
            # FIXME: Exception handling
            response = self.api_server.process_request(
                self, path, ChainMap(query, payload))

        else:
            IkaUtils.dprint('%s: Invalid REST API Request' % self)
            response = {'error': 'Invalid request'}

        if response is not None:
            if isinstance(response, Response):
                response.send(self)
            else:
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
        self._httpd = None

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
        self._httpd = ThreadedHTTPServer(
            (self._bind_addr, self._port), HTTPRequestHandler)
        self._httpd.ikalog_context = context
        self._httpd.parent = self
        self._httpd.serve_forever()
        IkaUtils.dprint('%s: finished serving' % self)

    def on_enable(self, context):
        self.initialize_server(context)

    def on_game_reset(self, context):
        # Update ikalog_context with the new context.
        if self._httpd:
            self._httpd.ikalog_context = context

    def on_uncaught_event(self, event_name, context, params=None):
        for listener in self._listeners:
            listener.on_event(event_name, context, params)

if __name__ == "__main__":
    host = 'localhost'
    port = 8000
    httpd = HTTPServer((host, port), HTTPRequestHandler)
    print('serving at port', port)
    httpd.serve_forever()
