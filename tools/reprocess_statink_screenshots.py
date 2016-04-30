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
import sqlite3
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


def query_statink_db(battle_id):
    #    battle_id = 1104044
    sql = 'SELECT id, battle_id, is_me, is_my_team, rank_in_team, level, rank, weapon, kill, death, point FROM battle_player WHERE battle_id=%d;' % battle_id
    print(sql)
    rows = db_battles.execute(sql)
    r = [None, None, None, None, None, None, None, None]
    for row in rows:
        row_id, battle_id_, is_me, is_my_team, rank_in_team, level, rank, weapon, kill, death, point = row
        team = 'my' if is_my_team else 'his'
        player_row = (1 - is_my_team) * 4 + rank_in_team - 1
        is_me = True if is_me else False
        r[player_row] = {
            'team': team,
            'is_me': is_me,
            'weapon': weapon,
            'rank': rank,
            'rank_in_team': rank_in_team,
            'level': level,
            'kill': kill,
            'death': death,
            'point': point,
            'row': player_row,
        }
    return r


def normalize_players(payload):
    r = [None, None, None, None, None, None, None, None]
    for p in payload['players']:
        is_my_team = 1 if p['team'] == 'my' else 0
        player_row = (1 - is_my_team) * 4 + p['rank_in_team'] - 1
        r[player_row] = p
    return r


def process_file(filename):
    context = {
        'engine': {'msec': 0,
                   'service': {'callPlugins': call_plugins_noop}},
        'game': {},
        'scenes': {},
        'lobby': {},
    }

    IkaUtils.dprint('Reading %s' % filename)
    context['engine']['frame'] = cv2.imread(filename, 1)

    assert context['engine']['frame'] is not None
    assert scene.match(context)
    assert scene.analyze(context)

    game_id = filename2statink_game_id(filename)
    assert game_id is not None
    me = IkaUtils.getMyEntryFromContext(context)

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
        if player.get('rank', False):
            if not player['rank'] in constants.udemae_strings:
                del player['rank']

    return context, payload


def logprint(text):
    print(text)

db_battles = sqlite3.connect('/home/hasegaw/battles/battles.db')

for filename in sys.argv[1:]:
    try:
        context, payload = process_file(filename)
    except AssertionError:
        print('AssertionError at %s' % filename)
        continue
    # except:
    #    print('UnExpected error at %s' % filename)
    #    continue

    if payload is None:
        print('Re-detection failed at %s' % filename)
        continue

    players_statink = query_statink_db(payload['id'])
    players_new = normalize_players(payload)
    battle_id = int(payload['id'])

    if payload is None:
        print('Re-detection failed at %s' % filename)

    for i in range(8):
        # Compare values
        n = players_new[i]
        s = players_statink[i]

        if (n is None) or (s is None):
            if (n is None) and (s is None):
                # Private match or squid match, not changed
                continue
            elif (n is None):
                # Player disappered
                logprint('battle %d player %d: Deleted' % (battle_id, i))
                continue
            elif (s is None):
                # Player added
                logprint('battle %d player %d: Add' % (battle_id, i))
                pass

        diff = False
        weapon_diff = False

        for key in ['rank', 'level', 'weapon', 'kill', 'death', 'point']:
            vs = s.get(key, None)
            ns = n.get(key, None)
            if str(vs) != str(ns):
                logprint('battle %d player %d: point %s -> %s' %
                         (battle_id, i, s.get(key, None), n.get(key, None)))
                diff = True
                if key == 'weapon':
                    weapon_diff = True

        if weapon_diff:
            # find the original index number
            if context['game']['won']:
                orig_team = {'my': 1, 'his': 2}[n['team']]
            else:
                orig_team = {'my': 2, 'his': 1}[n['team']]

            orig_row = None
            for i in range(len(context['game']['players'])):
                z = context['game']['players'][i]

                if z.get('team', 0) == orig_team and z.get('rank_in_team') == n['rank_in_team']:
                    orig_row = i
            assert orig_row is not None

            # Write weapon image file.
            dirname = os.path.join('weapons_new', str(n['weapon']))
            filename = os.path.join(dirname, '%d_%d.png' %
                                    (battle_id, orig_row))
            try:
                os.makedirs(dirname)
            except:
                pass
            cv2.imwrite(filename, context['game'][
                        'players'][orig_row]['img_weapon'])

#    sys.exit()

    a = payload['id'] - (payload['id'] % 10000)
    b = a + 9999
    #log_filename = 'statink_rerecognition.%08d-%08d.json.txt' % (a, b)
    log_filename = 'statink_rerecognition/%08d.json.txt' % (payload['id'])
    payload_json = json.dumps(payload, separators=(',', ':')) + "\n"

    try:
        log_file = open(log_filename, 'a')
        log_file.write(payload_json)
        log_file.close()
    except:
        print('Error writing to logfile %s at %s' % (log_filename, filename))
