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
import time
import threading
import os

import cv2

# FIXME
connections = []
jpeg_latest = None


class PreviewRequestHandler(object):

    def __init__(self, http_handler):
        self._http_handler = http_handler
        self._plugin = http_handler.server.parent
        self._frame = None
        self._new_image = False

        self._http_handler.send_response(200)
        self._http_handler.send_header(
            'Content-type', 'multipart/x-mixed-replace; boundary=--frame_boundary')
        self._http_handler.end_headers()

        self._plugin._listeners.append(self)

        while True:
            time.sleep(0.1)

            if (self._frame is None):
                continue

            # FIXME: JPEG data should be shared among connections, for
            # performance
            result, jpeg = cv2.imencode('.jpg', self._frame)
            if not result:
                continue

            jpeg_length = len(jpeg)
            self.new_image = False

            self._http_handler.wfile.write(
                '--frame_boundary\r\n'.encode('utf-8'))
            self._http_handler.send_header('Content-type', 'image/jpeg')
            self._http_handler.send_header('Content-length', str(jpeg_length))
            self._http_handler.end_headers()
            self._http_handler.wfile.write(jpeg)

        self._plugin._listeners.remove(self)

    def on_event(self, event_name, context, params=None):

        if event_name == 'on_show_preview':
            self._frame = context['engine']['frame']
            self._new_image = (self._frame is not None)
