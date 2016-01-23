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

from ikalog.api.server import HTTPRequestHandler as BaseHTTPRequestHandler
from http.server import HTTPServer
import json
import logging
import time

import ikalog.constants
from ikalog.utils import *
from ikalog.utils.character_recoginizer import DeadlyWeaponRecoginizer

import cv2
import numpy as np
import umsgpack


class HTTPRequestHandler(BaseHTTPRequestHandler):

    def monitor_recoginize_deadly_weapons(self, path, payload, response_payload):
        sample_filename = None
        hit_ratio = response_payload['score'] / response_payload['total']

        if hit_ratio < 0.7:
            sample_filename = 'training/_deadly_weapons.%s.%s.%s.png' % (
                payload.get('game_language', None),
                response_payload['deadly_weapon'],
                time.time()
            )

        if sample_filename is not None:
            image1 = self.api_server._decode_deadly_weapons_image(payload)
            cv2.imwrite(sample_filename, image1)

        log_record = {
            'path': path,
            'game_language': payload.get('game_language', None),
            'deadly_weapon': response_payload['deadly_weapon'],
            'score': response_payload['score'],
            'total': response_payload['total'],
            'ratio': hit_ratio,
            'sample_filename': sample_filename,
        }

        print(log_record)

    def callback_func(self, path, payload, response_payload):
        handlers = {
            '/api/v1/recoginizer/deadly_weapon': self.monitor_recoginize_deadly_weapons,
        }

        if path in handlers:
            handlers[path](path, payload, response_payload)

    def __init__(self, *args, **kwargs):
        super(HTTPRequestHandler, self).__init__(*args, **kwargs)

if __name__ == "__main__":
    host = 'localhost'
    port = 8000
    httpd = HTTPServer((host, port), HTTPRequestHandler)
    print('serving at port', port)
    httpd.serve_forever()

