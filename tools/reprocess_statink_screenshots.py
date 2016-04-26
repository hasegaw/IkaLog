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

#  Command-line program to run rerecognition of sceenshots posted to
#  stat.ink.

import cv2
import json
import os
import pprint
import re
import time
import sys

from ikalog import scenes, constants
from ikalog.utils import IkaUtils
from ikalog.version import IKALOG_VERSION

scene = scenes.ResultDetail(None)

def call_plugins_noop(context, params):
    pass

def _set_values(fields, dest, src):
    for field in fields:

        f_type = field[0]
        f_statink = field[1]
        f_ikalog = field[2]

        if (f_ikalog in src) and (src[f_ikalog] is not None):
            if f_type == 'int':
                try:
                    dest[f_statink] = int(src[f_ikalog])
                except:  # ValueError
                    IkaUtils.dprint('%s: field %s failed: src[%s] == %s' % (
                        self, f_statink, f_ikalog, src[f_ikalog]))
                    pass
            elif f_type == 'str':
                dest[f_statink] = str(src[f_ikalog])
            elif f_type == 'str_lower':
                dest[f_statink] = str(src[f_ikalog]).lower()

def filename2statink_game_id(filename):
    dirname, filename_ = os.path.split(filename)

    try:
        statink_game_id = int(re.sub(r'-result\.png', r'', filename_))
        return statink_game_id

    except ValueError:
        return None

def process_file(filename):
    context = {
        'engine': { 'msec': 0,
            'service': { 'callPlugins': call_plugins_noop } },
        'game': {},
        'scenes': {},
        'lobby': {},
    }

    context['engine']['frame'] = cv2.imread(filename, 1)

    assert context['engine']['frame'] is not None
    assert scene.match(context)
    assert scene.analyze(context)

    game_id = filename2statink_game_id(filename)
    assert game_id is not None

    payload = {
        'id': game_id,
        'recognition_source': filename,
        'recognition_at': int(time.time()),
        'agent': 'IkaLog re-recognition',
        'agent_version': IKALOG_VERSION,
        'players': [],
    }

    for e in context['game']['players']:
        player = {}
        player['team'] = 'my' if (e['team'] == me['team']) else 'his'
        player['is_me'] = 'yes' if e['me'] else 'no'
        player['weapon'] = e['weapon']
        payload['players'].append(player)

        _set_values(
            [  # 'type', 'stat.ink Field', 'IkaLog Field'
                ['int', 'rank_in_team', 'rank_in_team'],
                ['int', 'kill', 'kills'],
                ['int', 'death', 'deaths'],
                ['int', 'level', 'rank'],
                ['int', 'point', 'score'],
                ['str_lower', 'rank', 'udemae_pre'],
            ], player, e)

        # Validation
        if not player['rank'] in constants.udemae_strings:
            del player['rank']

    return payload

for filename in sys.argv[1:]:
    try:
        payload = process_file(filename)
    except AssertionError:
        print('AssertionError at %s' % filename)
        continue
    except:
        print('UnExpected error at %s' % filename)
        continue

    if payload is None:
        print('Re-detection failed at %s' % filename)
        continue

    a = payload['id'] - (payload['id'] % 10000)
    b = a + 9999
    log_filename = 'statink_rerecognition.%08d-%08d.json.txt' % (a, b)
    payload_json = json.dumps(payload, separators=(',', ':')) + "\n"

    try:
        log_file = open(log_filename, 'a')
        log_file.write(payload_json)
        log_file.close()
    except:
        print('Error writing to logfile %s at %s' % (log_filename, filename))
