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

import cv2
import numpy as np
import umsgpack

# weapons.load_model()

weapons = WeaponRecoginizer()
weapons.load_model_from_file()
weapons.knn_train()


class IkaLogAPIHandler(SimpleHTTPRequestHandler):

    def weapon_recoginition_req(self, payload):

        response_payload = []
        for img_bytes in payload:
            img = cv2.imdecode(np.fromstring(img_bytes, dtype='uint8'), 1)
            cv2.imshow('img', img)
            cv2.waitKey(1)
            result, distance = weapons.match(img)

            # FIXME: 現状返ってくる key が日本語表記なので id に変換
            weapon_id = None
            for k in ikalog.constants.weapons:
                if ikalog.constants.weapons[k]['ja'] == result:
                    weapon_id = k

            response_payload.append({'weapon': weapon_id})

        mp_r_payload_bytes = umsgpack.packb(response_payload)
        mp_r_payload = ''.join(map(chr, mp_r_payload_bytes))

        body = json.dumps(response_payload)

        self.send_response(200)
        self.send_header('Content-type', 'text/html; charset=utf-8')
        self.send_header('Pragma', 'no-cache')
        self.send_header('Content-length', len(body))
        self.end_headers()
        self.wfile.write(bytearray(body, 'utf-8'))

    def do_POST(self):
        length = int(self.headers.get('content-length'))
        data = self.rfile.read(length)
        payload = umsgpack.unpackb(data)

        paths = {
            '/api/v1/recoginizer/weapon': self.weapon_recoginition_req,
        }
        func = paths.get(self.path, None)
        if func is not None:
            func(payload)
            return
        else:
            logging.warning('No handler found')

        SimpleHTTPRequestHandler.do_GET(self)


host = 'localhost'
port = 8000
httpd = HTTPServer((host, port), IkaLogAPIHandler)
print('serving at port', port)
httpd.serve_forever()
