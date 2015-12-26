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
import urllib3

import cv2
import numpy as np
import umsgpack

from ikalog.api import APIServer


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
            pool = urllib3.PoolManager()
            req = pool.urlopen(
                'POST',
                url_api,
                headers=http_headers,
                body=mp_payload,
            )
        except urllib3.exceptions.MaxRetryError:
            raise Exception('API Error: Failed to connect to API endpoint.')

        return json.loads(req.data.decode('utf-8'))

    def recoginize_weapons(self, weapons_list):
        payload = []

        for img_weapon in weapons_list:
            result, img_weapon_png = cv2.imencode('.png', img_weapon)
            payload.append(img_weapon_png.tostring())

        response = self._request_func(
            '/api/v1/recoginizer/weapon',
            payload,
        )

        # Validate the response.
        assert response is not None, 'NO API Response.'
        assert response.get('status', None) == 'ok', 'API Error.'

        # Decode the response.
        ret = []
        for entry in response['weapons']:
            ret.append(entry.get('weapon', None))

        return ret

    def __init__(self, base_uri=None, local_mode=False):
        if local_mode:
            self._request_func = self._local_request_func
            self._server = APIServer()
        else:
            assert base_uri is not None
            self._request_func = self._http_request_func
            self.base_uri = base_uri

        pass

if __name__ == "__main__":

    import urllib3
    payload = []
    files = [
        'training/weapons/L3リールガン/142693-result.4.png',
        'training/weapons/L3リールガン/142693-result.4.png',
        'training/weapons/L3リールガン/142706-result.0.png',
        'training/weapons/L3リールガン/142707-result.0.png',
        'training/weapons/L3リールガン/142708-result.0.png',
        'training/weapons/L3リールガン/142706-result.0.png',
        'training/weapons/L3リールガン/142707-result.0.png',
        'training/weapons/L3リールガン/142708-result.0.png',
    ]

    for filename in files:
        f = open(filename, 'rb')
        img_bytes = f.read()
        img = cv2.imdecode(np.fromstring(img_bytes, dtype='uint8'), 1)
        payload.append(img)
        f.close()

    # Test APIServer on this process
    client = APIClient(local_mode=True)
    print(client.recoginize_weapons(payload))

    # Test APIServer over HTTP
    client = APIClient(base_uri='http://localhost:8000')
    print(client.recoginize_weapons(payload))
