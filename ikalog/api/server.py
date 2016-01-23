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
import cgi
import json
import logging

import ikalog.constants
from ikalog.utils import *
from ikalog.utils.character_recoginizer import DeadlyWeaponRecoginizer

import cv2
import numpy as np
import umsgpack

# weapons.load_model()

weapons = WeaponRecoginizer()
weapons.load_model_from_file()
weapons.knn_train()


class APIServer(object):

    def _unpack_deadly_weapons_image(self, payload):
        h = payload['sample_height']
        w = payload['sample_width']
        lang = payload['game_language']
        img_bytes = payload['samples']
        samples1 = cv2.imdecode(np.fromstring(img_bytes, dtype='uint8'), 1)
        num_samples = int(samples1.shape[0] / h)

        last_image = None
        y = 0

        images = []

        deadly_weapon_recoginizer = DeadlyWeaponRecoginizer()

        votes = {}
        for i in range(num_samples):
            image = samples1[y: y + h, :]
            if last_image is None:
                last_image = np.array(image, dtype=np.uint8)
                current_image = image
            else:
                diff_image = image
                current_image = abs(last_image - diff_image)

            id = deadly_weapon_recoginizer.match(current_image)

            votes[id] = votes.get(id, 0) + 1
            y = y + h

        best_result = (None, 0)
        for weapon_id in votes.keys():
            if votes[weapon_id] > best_result[1]:
                best_result = (id, votes[weapon_id])
        response_payload = {
            'status': 'ok',
            'deadly_weapon': best_result[0],
            'score': best_result[1],
            'total': num_samples,
        }

        return response_payload

    def recoginize_deadly_weapons(self, payload):
        response_payload = self._unpack_deadly_weapons_image(payload)
        return response_payload

    def recoginize_weapons(self, payload):
        weapons_list = []
        for img_bytes in payload:
            img = cv2.imdecode(np.fromstring(img_bytes, dtype='uint8'), 1)
            assert img is not None
            result, distance = weapons.match(img)

            # FIXME: 現状返ってくる key が日本語表記なので id に変換
            weapon_id = None
            for k in ikalog.constants.weapons:
                if ikalog.constants.weapons[k]['ja'] == result:
                    weapon_id = k

            weapons_list.append({'weapon': weapon_id})

        response_payload = {
            'status': 'ok',
            'weapons': weapons_list,
        }

        return response_payload

    def process_request(self, path, payload):
        handler = {
            '/api/v1/recoginizer/weapon': self.recoginize_weapons,
            '/api/v1/recoginizer/deadly_weapon': self.recoginize_deadly_weapons,
        }.get(path, None)

        if handler is None:
            raise Exception('Invalid API Path %s' % path)

        response_payload = handler(payload)

        if hasattr(self, 'callback_func'):
            self.callback_func(path, payload, response_payload)

        return response_payload


class HTTPRequestHandler(SimpleHTTPRequestHandler):

    def _send_response_json(self, response):
        body = json.dumps(response)

        self.send_response(200)
        self.send_header('Content-type', 'text/html; charset=utf-8')
        self.send_header('Pragma', 'no-cache')
        self.send_header('Content-length', len(body))
        self.end_headers()
        self.wfile.write(bytearray(body, 'utf-8'))

    def do_POST(self):
        length = int(self.headers.get('content-length'))
        data = self.rfile.read(length)

        # FIXME: support both of msgpack and JSON format.
        payload = umsgpack.unpackb(data)

        # FixMe: catch expcetion.
        response = self._server.process_request(
            self.path,
            payload)

        self._send_response_json(response)

    def __init__(self, *args, **kwargs):
        self._server = APIServer()
        super(HTTPRequestHandler, self).__init__(*args, **kwargs)

if __name__ == "__main__":
    host = 'localhost'
    port = 8000
    httpd = HTTPServer((host, port), HTTPRequestHandler)
    print('serving at port', port)
    httpd.serve_forever()
