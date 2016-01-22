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
from ikalog.utils import Localization


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

    def pack_deadly_weapons_image(self, deadly_weapons_list):
        h = deadly_weapons_list[0].shape[0]
        w = deadly_weapons_list[0].shape[1]
        print('%s: %d samples, dimension = %s' %
              (self, len(deadly_weapons_list), (w, h)))

        out_orig_image = np.zeros(
            (h * len(deadly_weapons_list), w), dtype=np.uint8)
        out_image = np.zeros((h * len(deadly_weapons_list), w), dtype=np.uint8)
        out_decode_image = np.zeros(
            (h * len(deadly_weapons_list), w, 3), dtype=np.uint8)

        last_image = None
        y = 0
        for image in deadly_weapons_list:
            if len(image.shape) == 3:
                image = image[:, :, 0]

            if last_image is None:
                last_image = image
                current_image = image
                diff_image = image
            else:
                current_image = image
                diff_image = abs(last_image - current_image)

            out_image[y: y + h, :] = diff_image
            out_orig_image[y: y + h, :] = current_image

            decoded_image = abs(last_image - out_image[y:y + h, :])
            out_decode_image[y: y + h, :, 0] = decoded_image
            out_decode_image[y: y + h, :, 1] = current_image

            y = y + h
        if 0:
            cv2.imshow('out', out_image)
            cv2.imshow('decoded', out_decode_image)
            # cv2.imshow('check', abs(out_decode_image - out_orig_image))
            cv2.waitKey()

        return out_image

    def recoginize_deadly_weapons(self, deadly_weapons_list):
        if len(deadly_weapons_list) == 0:
            return None
        images = self.pack_deadly_weapons_image(deadly_weapons_list)

        payload = {
            'game_language': Localization.get_game_languages()[0],
            'sample_height': deadly_weapons_list[0].shape[0],
            'sample_width': deadly_weapons_list[0].shape[1],
            'samples': cv2.imencode('.png', images)[1].tostring()
        }

        response = self._request_func(
            '/api/v1/recoginizer/deadly_weapon',
            payload,
        )

        if response.get('status', None) != 'ok':
            return {'status': 'error'}

        return response

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
