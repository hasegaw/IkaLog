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

from http.server import HTTPServer, SimpleHTTPRequestHandler
import os
import pprint
import re
import time
import sys
import traceback

import cv2
import json
import umsgpack
import numpy as np

from ikalog import scenes, constants
from ikalog.utils import IkaUtils
from ikalog.version import IKALOG_VERSION

scene = scenes.ResultDetail(None)


def logprint(text):
    print(text)

# Dummy call_plugins_handler.


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


# SQLite3 DB Adapter
#
class StatInkDB_SQLite(object):

    # query battle_player rows for the battle specified in battle_id
    def select_battle_player_by_battle_id(self, battle_id):
        sql = 'SELECT id, battle_id, is_me, is_my_team, rank_in_team, level, rank, weapon, kill, death, point FROM battle_player WHERE battle_id=%d;' % battle_id
        print(sql)
        rows = self.db_battles.execute(sql)

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

    def __init__(self, database_file):
        import sqlite3
        self.db_battles = sqlite3.connect('/home/hasegaw/battles/battles.db')


class StatInkRecordComparator(object):

    # Reorder the players in payload['players']
    # In stat.ink battle POST format, index number of each players are lost.
    # To compare each player entries, this function normalizes the list.
    #
    #  r[0]: team=my,  rank_in_team=1
    #  r[1]: team=my,  rank_in_team=2
    #  r[2]: team=my,  rank_in_team=3
    #  r[3]: team=my,  rank_in_team=4
    #  r[4]: team=his, rank_in_team=1
    #  r[5]: team=his, rank_in_team=2
    #  r[6]: team=his, rank_in_team=3
    #  r[7]: team=his, rank_in_team=4
    #
    # r[0 <= i <= 7] can be either of dict (of stat.ink player format),
    # or None. None indicates the data doesn't have corresponding entry.
    @staticmethod
    def reorder_battle_players(battle_players_list):
        r = [None] * 8

        for p in battle_players_list:
            # Validation
            if p is None:
                continue
            if not (p.get('team', None) in [1, 2]):
                continue
            if not (p.get('rank_in_team', None) in [1, 2, 3, 4]):
                continue

            # Copy the reference to the pow
            is_my_team = 1 if p['team'] == 'my' else 0
            player_row = (1 - is_my_team) * 4 + p['rank_in_team'] - 1
            r[player_row] = p

        return r

    # Reorder the players in payload['players'] in original order.
    @staticmethod
    def reorder_battle_players_by_original_order(battle_players_list, won):
        r = [None] * 8

        for p in battle_players_list:
            team = p.get('team', None)
            if not (team in ['my', 'his']):
                continue

            rank_in_team = p.get('rank_in_team', None)
            if not (rank_in_team in [1, 2, 3, 4]):
                continue

            if won:
                orig_team = {'my': 1, 'his': 2}[team]
            else:
                orig_team = {'my': 2, 'his': 1}[team]

            orig_row = (orig_team - 1) * 4 + (rank_in_team - 1)
            r[orig_row] = p
        return r

    # Compare player data in two dictionaries. If a empty dictionary is
    # returned, the data is identical. If the dictionary has key-values,
    # key indicates the what is differ between two given dictionaries,
    # and its 1st/2nd value in the tuple indicates 2nd/1st value.
    #
    # Result format:
    # r = {
    #   'weapon': ('sshooter_wasabi', 'sshooter_collabo'),
    #   'kill': (7, 1),
    # }
    #
    # tuple format: (new_value, old_value)
    #
    # The example describes:
    # - Player data A and B is given
    # - Player A has value of weapon: sshooter_collabo, and 1 kill
    # - Player B has value of weapon: sshooter_wasabi, and 7 kills
    @classmethod
    def _compare_battle_player(self, p1, p2, keys=None, show_diff=None):
        # FIXME: battle_id and i doesn't work
        battle_id = 0
        i = 0
        r = {}

        if not keys:
            keys = ['rank', 'level', 'weapon', 'kill', 'death', 'point']

        for key in keys:
            val1 = p1.get(key, None)
            val2 = p2.get(key, None)
            if str(val1) != str(val2):
                r[key] = (val2, val1)
                if show_diff:
                    logprint('battle %d player %d: %s %s -> %s' %
                             (battle_id, i, key, val1, val2))
        return r

    # compare_battle_players
    # Compare the context of battle_players table between 'old' and 'new'
    #
    # Both data should be encoded in stat.ink battle POST format.
    @classmethod
    def compare_battle_players(self, d1, d2):
        # FIXME: battle_id
        battle_id = 0

        # Reorder players to compare
        players1 = StatInkRecordComparator.reorder_battle_players(d1[
                                                                  'players'])
        players2 = StatInkRecordComparator.reorder_battle_players(d2[
                                                                  'players'])

        r = [None] * 8

        for i in range(len(players2)):
            player1 = players1[i]
            player2 = players2[i]

            if (player1 is None) or (player2 is None):
                if (player1 is None) and (player2 is None):
                    # player doesn't exist in both of player1 and player2. Skip
                    continue

                elif (player1 is not None) and (player2 is None):
                    # Player disappered.
                    logprint('battle %d player %d: Deleted' % (battle_id, i))
                    continue

                elif (player2 is not None):
                    # Player added
                    logprint('battle %d player %d: Add' % (battle_id, i))

            # compare values.
            r[i] = self._compare_battle_player(
                player1, player2, show_diff=True)

        return r


class ScoreBoardRecognition(object):

    # If there is a change in weapon classification, save the
    # image.
    def on_battle_player_weapon_changed(self, context, player_index):
        # FIXME: needs fix. not working
        # Write weapon image file.
        dirname = os.path.join('weapons_new', str(n['weapon']))
        filename = os.path.join(dirname, '%d_%d.png' % (battle_id, orig_row))

        try:
            os.makedirs(dirname)
        except:
            pass
        cv2.imwrite(filename, context['game'][
                    'players'][orig_row]['img_weapon'])

    # Tiny stat.ink payload composition, for re-recognition
    def composite_payload(self, context):
        payload = {
            # 'id': game_id,
            #'recognition_source': filename,
            'recognition_at': int(time.time()),
            'agent': 'IkaLog re-recognition',
            'agent_version': IKALOG_VERSION,
            'players': [],
        }

        me = IkaUtils.getMyEntryFromContext(context)

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

        return payload

    def process_scoreboard(self, frame, battle_id=None):
        scene = scenes.ResultDetail(None)  # FIXME: Reuse the instance
        context = {
            'engine': {
                'msec': 0,
                'frame': frame,
                'service': {'callPlugins': call_plugins_noop},
            },
            'game': {},
            'scenes': {},
            'lobby': {},
        }

        matched = scene.match(context)
        analyzed = None
        if matched:
            analyzed = scene.analyze(context)

        assert matched
        assert analyzed

        # Composite stat.ink payload
        payload = self.composite_payload(context)

        # If applicable, query stat.ink result and compare.
        compare_with_statink = 1

        if compare_with_statink:
            compare_with_statink = (self.db_statink is not None) and (
                battle_id is not None)

        if compare_with_statink:
            statink_data = {}
            statink_data['players'] = self.db_statink.select_battle_player_by_battle_id(
                battle_id=battle_id)
            diff = StatInkRecordComparator.compare_battle_players(
                statink_data, payload)
        else:
            diff = [{}] * len(payload['players'])

        # We need to know player's original row in the image
        players_in_original_order = StatInkRecordComparator.reorder_battle_players_by_original_order(
            payload['players'],
            won=context['game']['won'],
        )

        # Do actions for each player's change
        for i in range(len(diff)):
            pdiff = diff[i]
            if pdiff is None:
                continue

            p = payload['players'][i]
            orig_row = players_in_original_order.index(p)

            if 'weapon' in pdiff:
                if hasattr(self, 'on_battle_player_weapon_changed'):
                    pass
                    # self.on_battle_player_weapon_changed(context, orig_row)

        return payload

    # Apply commandline arguments
    def apply_arguments(self, args):
        print(args)
        if args.db_file:
            self.db_statink = StatInkDB_SQLite(args.db_file)

    # Constructor.
    def __init__(self):
        self.db_statink = None


# HTTPRequestHandler for server mode.
#
class HTTPRequestHandler(SimpleHTTPRequestHandler):

    def scoreboard_recognition(self, payload):
        frame = cv2.imdecode(np.fromstring(
            payload['image_result'], dtype='uint8'), 1)

        assert frame.shape[0] == 720
        assert frame.shape[1] == 1280
        assert frame.shape[2] == 3

        return self._scoreboard_recognition.process_scoreboard(frame)

    def dispatch_request(self, path, payload):
        handler = {
            '/api/v1/scoreboard_recognition': self.scoreboard_recognition,
        }.get(path, None)

        if handler is None:
            return {'status': 'error', 'description': 'Invalid API Path %s' % path}

        try:
            response_payload = handler(payload)
        except Exception as e:
            return {'status': 'error', 'description': str(e), 'detail': traceback.format_exc()}

        return response_payload

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
        response = self.dispatch_request(self.path, payload)

        self._send_response_json(response)

        if hasattr(self, 'callback_func'):
            self.callback_func(self.path, payload, response)

    def __init__(self, *args, **kwargs):
        self._scoreboard_recognition = ScoreBoardRecognition()

        super(HTTPRequestHandler, self).__init__(*args, **kwargs)


# Run HTTP Server for remote requests.
#
def _run_server(args):
    print(args)
    httpd = HTTPServer((args.bind_addr, args.bind_port), HTTPRequestHandler)
    # httpd._scoreboard_recognition.apply_arguments(args)

    print('serving at port', args.bind_port)
    httpd.serve_forever()

# Extract battle_id from stat.ink screenshot filename.


def _filename2battle_id(filename):
    dirname, filename_ = os.path.split(filename)

    try:
        battle_id = int(re.sub(r'-result\.png', r'', filename_))
        return battle_id
    except ValueError:
        return None


# Process local screenshot and write the result.
#
# In local mode, there are two additional data:
#   id:                 stat.ink battle_id
#   recognition_source: source filename processed


def _process_local_file(obj, args, filename):
    battle_id = args.battle_id or _filename2battle_id(filename)

    # process
    frame = cv2.imread(filename, 1)

    # write
    log_filename = 'statink_rerecognition/%08d.json.txt' % (battle_id)

    payload = obj.process_scoreboard(frame, battle_id=battle_id)
    if battle_id:
        payload['id'] = battle_id
    payload['recognition_source'] = filename

    payload_json = json.dumps(payload, separators=(',', ':')) + "\n"
    try:
        log_file = open(log_filename, 'a')
        log_file.write(payload_json)
        log_file.close()
        print('wrote %s at %s' % (log_filename, filename))
    except:
        print('Error writing to logfile %s at %s' % (log_filename, filename))

# Argument Parser


def _get_args():
    import argparse
    parser = argparse.ArgumentParser()
    parser.add_argument('--bind', '-b', dest='bind_addr',
                        type=str, default='localhost')
    parser.add_argument('--port', '-p', dest='bind_port',
                        type=int, default=8888)
    parser.add_argument('--server', '-s', dest='run_server',
                        action='store_true', default=False)
    parser.add_argument('--battle_id', type=int,
                        default=None, help='stat.ink battle ID')
    parser.add_argument('--input_file', default=None,
                        help='1280x720 image file to process')
    parser.add_argument('--db_file', default=None,
                        help='stat.ink SQLite3 filename')

    return parser.parse_args()

if __name__ == "__main__":
    args = _get_args()

    if args.run_server:
        _run_server(args)
        sys.exit(0)

    elif args.input_file:
        # FIXME: Support batched mode
        print('input file %s' % args.input_file)

        obj = ScoreBoardRecognition()
        obj.apply_arguments(args)

        _process_local_file(obj, args, args.input_file)
        sys.exit(0)

    print('Nothing to do.')
