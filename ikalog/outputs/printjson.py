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
import os
import time

from ikalog.plugin import IkaLogPlugin
from ikalog.utils import *

_ = Localization.gettext_translation('json', fallback=True).gettext


def _set(dest, dest_key, src, src_key):
    if src_key not in src:
        return
    dest[dest_key] = src[src_key]


def _append_file(filename, text):
    with open(filename, 'a') as file:
        file.write(text)

"""
JSON Data Manupulation
"""


def _result_scoreboard2json_game(context):
    game = context.get('game', {})
    map = game.get('map')
    rule = game.get('rule')
    won = IkaUtils.getWinLoseText(
        game.get('won'), win_text='win', lose_text='lose', unknown_text='unknown')

    t_unix = int(IkaUtils.get_end_time(context).timestamp())

    record = {
        'time': t_unix,
        'event': 'GameResult',
        'map': map,
        'rule': rule,
        'result': won
    }

    # Cash
    result_gears = context['scenes'].get('result_gears', {})
    if context['scenes'].get('result_gears'):
        _set(record, 'cash_after', result_gears, 'cash')

    return record


def _result_scoreboard2json_lobby(context, record):
    game = context.get('game', {})
    ctx_lobby = context.get('lobby', {})
    _set(record, 'lobby', ctx_lobby, 'type')

    if (not record.get('lobby')) and game.get('is_fes'):
        record['lobby'] = 'festa'

    return True


def _result_scoreboard2json_ranked_battle(context, record):
    game = context.get('game', {})

    _set(record, 'udemae_pre', game, 'result_udemae_str_pre')
    _set(record, 'udemae_exp_pre', game, 'result_udemae_exp_pre')
    _set(record, 'udemae_after', game, 'result_udemae_str')
    _set(record, 'udemae_exp_after', game, 'result_udemae_exp')
    return True


def _result_scoreboard2json_players(context, record):
    fields = ['team', 'kills', 'deaths', 'score', 'weapon', 'rank_in_team']

    me = IkaUtils.getMyEntryFromContext(context)
    game = context['game']
    game_players = game.get('players', [])

    if me:
        for field in fields:
            _set(record, field, me, field)

    players_json = []
    for player in game_players:
        player_record = {}
        for field in fields:
            _set(player_record, field, player, field)
        players_json.append(player_record)

    if len(players_json) > 0:
        record['players'] = players_json

    return True


def _result_scoreboard2json(context):
    record = _result_scoreboard2json_game(context)
    _result_scoreboard2json_lobby(context, record)
    _result_scoreboard2json_ranked_battle(context, record)
    _result_scoreboard2json_players(context, record)
    return record


class JSONPlugin(IkaLogPlugin):

    """
    Configuration read/write
    """
    plugin_name = "JSON"

    def on_validate_configuration(self, config):
        assert config['enabled'] in [True, False]
        assert config['filename'] is not None
        return True

    def on_reset_configuration(self):
        self.config['filename'] = ''
        self.config['enabled'] = False

    def on_set_configuration(self, config):
        self.config['filename'] = config['filename']
        self.config['enabled'] = config['enabled']

    """
    Session management
    """

    def _open_game_session(self, context):
        self._called_close_game_session = False

    """
    IkaLog event handlers
    """

    def on_game_go_sign(self, context):
        self._open_game_session(context)

    def on_game_start(self, context):
        # Fallback in the case on_game_go_sign was skipped.
        self._open_game_session(context)

    def _close_game_session(self, context):
        if self._called_close_game_session:
            return
        self._called_close_game_session = True

        IkaUtils.dprint('%s (enabled = %s)' % (self, self.config['enabled']))
        if not self.config['enabled']:
            return

        record = _result_scoreboard2json(context)
        record_1line = json.dumps(record, separators=(',', ':')) + '\n'
        try:
            _append_file(self.config['filename'], record_1line)
        except:  # FIXE
            IkaUtils.dprint('CSV: Failed to write JSON File')
            IkaUtils.dprint(traceback.format_exc())

    def on_game_session_end(self, context):
        self._close_game_session(context)

    def on_game_session_abort(self, context):
        self._close_game_session(context)

    def __init__(self):
        super(JSONPlugin, self).__init__()
        # If true, it means the data is not saved.
        self._called_close_game_session = False


class LegacyJSON(JSONPlugin):

    def __init__(self, json_filename=None, append_data=True):
        super(LegacyJSON, self).__init__()
        config = {'enabled':  (not json_filename is None),
                  'filename': json_filename,
                  'append_data': append_data,
                  }
        self.set_configuration(config)

JSON = LegacyJSON
