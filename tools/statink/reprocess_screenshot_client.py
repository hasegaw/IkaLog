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

import json
import pprint
import urllib3

import cv2
import numpy as np
import umsgpack

from ikalog.api import APIServer
from ikalog.utils import Localization, IkaUtils


class APIClient(object):

    def _local_request_func(self, path, payload):
        return self._server.process_request(path, payload)

    def _http_request_func(self, path, payload):
        url_api = '%s%s' % (self.base_uri, path)
        http_headers = {
            'Content-Type': 'application/x-msgpack',
        }
        mp_payload = ''.join(map(chr, umsgpack.packb(payload)))

        try:
            pool = urllib3.PoolManager(timeout=10.0)
            req = pool.urlopen(
                'POST',
                url_api,
                headers=http_headers,
                body=mp_payload,
            )
            return json.loads(req.data.decode('utf-8'))

        except urllib3.exceptions.MaxRetryError:
            fallback = self._fallback  # or .... or ...

            if fallback:
                IkaUtils.dprint(
                    '%s: Remote API Error. Falling back to local mode' % self)
                return self._local_request_func(path, payload)

        raise Exception(
            'API Error: Failed to connect to API endpoint. (No fallback)')

    def scoreboard_recognition(self, img_result):
        result, img_result_png = cv2.imencode('.png', img_result)
        payload = {
            'image_result': img_result_png.tostring(),
        }

        response = self._request_func(
            '/api/v1/scoreboard_recognition',
            payload,
        )

#        if response.get('status', None) != 'ok':
#            return {'status': 'error'}

        return response

    def __init__(self, base_uri=None, local_mode=False, fallback=True):
        self._server = APIServer()

        if local_mode:
            self._request_func = self._local_request_func
        else:
            assert base_uri is not None
            self._request_func = self._http_request_func
            self.base_uri = base_uri
            self._fallback = fallback

if __name__ == "__main__":
    import sys

    client = APIClient(base_uri='http://localhost:8888')
    for filename in sys.argv[1:]:
        img = cv2.imread(filename, 1)
        response = client.scoreboard_recognition(img)
        pprint.pprint(response)
