#!/usr/bin/env python3
# -*- coding: utf-8 -*-
#
#  IkaLog
#  ======
#  Copyright (C) 2016 Takeshi HASEGAWA
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
import os
import sys
import time
import umsgpack
import urllib3

from ikalog.utils import *


def UploadToStatInk(payload, api_key, url=None, video_id=None,
                    show_response=False, dry_run=False):
    name = 'UploadToStatInk'
    if not url:
        url = 'https://stat.ink/api/v1/battle'

    # Payload data will be modified, so we copy it.
    # It is not deep copy, so only dict object is duplicated.
    payload = payload.copy()
    payload['apikey'] = api_key
    if dry_run:
        payload['test'] = 'dry_run'
    if video_id:
        payload['link_url'] = 'https://www.youtube.com/watch?v=%s' % video_id

    mp_payload_bytes = umsgpack.packb(payload)
    mp_payload = ''.join(map(chr, mp_payload_bytes))

    http_headers = {
        'Content-Type': 'application/x-msgpack',
    }

    IkaUtils.dprint('%s: POST %s' % (name, url))
    time_post_start = time.time()

    pool = urllib3.PoolManager(
        cert_reqs='CERT_REQUIRED',  # Force certificate check
        ca_certs=Certifi.where(),   # Path to the Certifi bundle.
        timeout=120.0,              # Timeout (in sec)
    )

    # Post the payload

    try:
        req = pool.urlopen('POST', url,
                           headers=http_headers,
                           body=mp_payload,
                           )
    except urllib3.exceptions.SSLError as e:
        # Handle incorrect certificate error.
        IkaUtils.dprint('%s: SSLError, value: %s' % (name, e.value))

    # Error detection

    error = False
    try:
        statink_response = json.loads(req.data.decode('utf-8'))
        error = 'error' in statink_response
        if error:
            IkaUtils.dprint('%s: API Error occured')
    except:
        error = True
        IkaUtils.dprint('%s: Stat.ink return non-JSON response')
        statink_response = {
            'error': 'Not a JSON response',
        }

    # Debug messages

    if show_response or error:
        IkaUtils.dprint('%s: == Response begin ==' % name)
        print(req.data.decode('utf-8'))
        IkaUtils.dprint('%s: == Response end ===' % name)

    IkaUtils.dprint(
        '%s: POST Done. %d bytes in %f second(s).' % (
            name,
            len(mp_payload),
            int((time.time() - time_post_start) * 10) / 10,
        )
    )
    IkaUtils.dprint(statink_response.get('url'))

    return [error, statink_response]
