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

import pprint

import umsgpack
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
    payload.append(f.read())
    f.close()


mp_payload_bytes = umsgpack.packb(payload)
mp_payload = ''.join(map(chr, mp_payload_bytes))

url_api = 'http://localhost:8000/api/v1/recoginizer/weapon'
http_headers = {
    'Content-Type': 'application/x-msgpack',
}

pool = urllib3.PoolManager()
req = pool.urlopen('POST', url_api,
                   headers=http_headers,
                   body=mp_payload,
                   )

print(req.data.decode('utf-8'))
