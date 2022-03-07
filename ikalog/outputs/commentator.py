#!/usr/bin/env python3
# -*- coding: utf-8 -*-
#
#  IkaLog
#  ======
#  Copyright (C) 2015 ExceptionError
#  Copyright (C) 2015 Takeshi HASEGAWA
#  Copyright (C) 2015 AIZAWA Hina
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
import random
import select
import socket
import sys
import traceback
import threading
import os
import csv

from ikalog.constants import *
from ikalog.utils import *

class CommentatorDictionary(object):
    '''
    実況アプリ用辞書
    '''

    _config = {}

    def __init__(self, config, csv_path):
        if csv_path is None:
            csv_path = os.path.join(
                os.path.dirname(__file__),
                '..', '..', 'tools', 'commentator.csv'
            )

        self._load_csv(csv_path)

        for key in config:
            self._config[key] = config[key]

    def _load_csv(self, path):
        try:
            IkaUtils.dprint(
                'Commentator(Boyomi/MikuMikuMouth): Dictionary load from csv {path}'.format(path=path)
            )
            with open(path, 'r', encoding="utf_8_sig") as fh:
                reader = csv.reader(fh)
                for row in reader:
                    if len(row) < 2:
                        continue

                    event_name = row[0].strip()
                    text = row[1].strip()
                    emotion = row[2].strip() if len(row) >= 3 else 'none'

                    if event_name.startswith('#'):
                        continue

                    if event_name not in self._config:
                        self._config[event_name] = []

                    self._config[event_name].append({'text': text, 'emotion': emotion})

        except FileNotFoundError:
            error = 'Commentator(Boyomi/MikuMikuMouth): CSV file "{path}" does not exist.'.format(path=path)
            IkaUtils.dprint(error)

    def data(self, key):
        default_messages = [{'text': '', 'emotion': 'none'}]
        return random.choice(self._config.get(key, default_messages)).copy()

    def get_config(self):
        return self._config


class Commentator(object):
    '''
    実況者基底クラス
    '''
    custom_read = {
        'unknown': '未知の武器',
    }

    def __init__(self, dictionary={}, dictionary_csv=None, custom_read_csv=None):
        self._enabled = True
        self._dict = CommentatorDictionary(dictionary, dictionary_csv)
        if custom_read_csv is None:
            custom_read_csv = os.path.join(
                os.path.dirname(__file__),
                '..', '..', 'tools', 'custom_read.csv'
            )

        self._load_custom_read_csv(custom_read_csv)

    def _load_custom_read_csv(self, path):
        try:
            IkaUtils.dprint(
                'Commentator(Boyomi/MikuMikuMouth): Custom-read data load from csv {path}'.format(path=path)
            )
            with open(path, 'r', encoding="utf_8_sig") as fh:
                reader = csv.reader(fh)
                for row in reader:
                    if len(row) < 2:
                        continue

                    reason = row[0].strip()
                    text = row[1].strip()

                    if reason.startswith('#'):
                        continue

                    self.custom_read[reason] = text

        except FileNotFoundError:
            error = 'Commentator(Boyomi/MikuMikuMouth): CSV file "{path}" does not exist.'.format(path=path)
            IkaUtils.dprint(error)

    def set_config(self, config):
        dictionary = config.get(self.config_key(), {})
        self._dict = CommentatorDictionary(dictionary)

    def get_config(self, config):
        commentator = self._dict.get_config()
        config[self.config_key()] = commentator
        return config

    def _read(self, message):
        if (not self._enabled) or (message is None) or (len(message['text']) == 0):
            return

        try:
            self._do_read(message)
        except ConnectionRefusedError:
            error = '「{message}」を読み上げることができませんでした'.format(message=message['text'])
            IkaUtils.dprint(traceback.format_exc())

    def _do_read(self, message):
        return

    def _get_message(self, key):
        return self._dict.data(key)

    def _read_event(self, key):
        self._read(self._get_message(key))

    def on_lobby_matching(self, context):
        self._read_event('lobby_matching')

    def on_lobby_matched(self, context):
        self._read_event('lobby_matched')

    def on_game_start(self, context):
        map_text = IkaUtils.map2text(context['game']['map'], unknown='スプラトゥーン', languages='ja')
        rule_text = IkaUtils.rule2text(context['game']['rule'], unknown='ゲーム', languages='ja')
        data = self._get_message('start')
        data['text'] = data['text'].format(map=map_text, rule=rule_text)
        self._read(data)

    def on_game_go_sign(self, context):
        self._read_event('go_sign')

    def on_game_killed(self, context, params):
        self._read_event('killed')

    def on_game_dead(self, context):
        self._read_event('dead')

    def on_game_death_reason_identified(self, context):
        reason = context['game']['last_death_reason']
        if reason in oob_reasons:
            data = self._get_message('death_reason_oob')
        else:
            label = self._death_reason_label(reason)
            data = self._get_message('death_reason_identified')
            data['text'] = data['text'].format(reason=label)
        self._read(data)

    def _death_reason_label(self, reason):
        if reason in self.custom_read:
            return self.custom_read[reason]
        return IkaUtils.death_reason2text(
            reason, self.custom_read['unknown'], 'ja')

    def on_game_low_ink(self, context):
        self._read_event('low_ink')

    def on_game_special_gauge_charged(self, context):
        self._read_event('special_charged')

    def on_game_special_weapon(self, context, params={}):
        special_weapon = params['special_weapon']
        if special_weapon not in special_weapons.keys():
            return

        my_event = params['me']
        data = self._get_message(
            'my_special_weapon' if my_event else 'mate_special_weapon'
        )
        if data['text'] == '':
            return

        data['text'] = data['text'].format(
            weapon=self._special_weapon_name(special_weapon)
        )
        self._read(data)

    def _special_weapon_name(self, special):
        return self._death_reason_label(special)

    def on_game_finish(self, context):
        self._read_event('finish')

    def on_game_individual_result(self, context):
        map = IkaUtils.map2text(context['game']['map'])
        rule = IkaUtils.rule2text(context['game']['rule'])
        won = IkaUtils.getWinLoseText(
            context['game']['won'],
            win_text=self._get_message('individual_result_win'),
            lose_text=self._get_message('individual_result_lose'),
            unknown_text=self._get_message('individual_result_unknown')
        )
        self._read(won)

        me = IkaUtils.getMyEntryFromContext(context)
        kill = me['kills']
        death = me['deaths']
        data = self._get_message('individual_kill_death')
        if data['text'] != '':
            data['text'] = data['text'].format(kill=kill, death=death)
            self._read(data)

        if (me.get('score') is not None) and (context['game']['won'] is not None):
            # 判定のしようもないので、300pt時代のことは考えない
            bonus = 1000 if context['game']['won'] else 0
            score = int(me['score'])
            inked = score - bonus
            if inked > 0:
                data = self._get_message('individual_score')
                if data['text'] != '':
                    data['text'] = data['text'].format(
                        score=score,
                        inked=inked,
                        bonus=bonus
                    )
                    self._read(data)

    def on_game_session_end(self, context):
        self._read_event('session_end')

    def on_game_session_abort(self, context):
        self._read_event('session_abort')

    def on_game_ranked_we_lead(self, context):
        self._read_event('ranked_we_lead')

    def on_game_ranked_they_lead(self, context):
        self._read_event('ranked_they_lead')

    def on_game_splatzone_we_got(self, context):
        self._read_event('splatzone_we_got')

    def on_game_splatzone_we_lost(self, context):
        self._read_event('splatzone_we_lost')

    def on_game_splatzone_they_got(self, context):
        self._read_event('splatzone_they_got')

    def on_game_splatzone_they_lost(self, context):
        self._read_event('splatzone_they_lost')

    def on_game_rainmaker_we_got(self, context):
        self._read_event('rainmaker_we_got')

    def on_game_rainmaker_we_lost(self, context):
        self._read_event('rainmaker_we_lost')

    def on_game_rainmaker_they_got(self, context):
        self._read_event('rainmaker_they_got')

    def on_game_rainmaker_they_lost(self, context):
        self._read_event('rainmaker_they_lost')

    def on_game_tower_we_got(self, context):
        self._read_event('tower_we_got')

    def on_game_tower_we_lost(self, context):
        self._read_event('tower_we_lost')

    def on_game_tower_they_got(self, context):
        self._read_event('tower_they_got')

    def on_game_tower_they_lost(self, context):
        self._read_event('tower_they_lost')

    def on_salmonrun_egg_delivered(self, context, params):
        self._read_event('salmonrun_egg_delivered')

    def on_salmonrun_game_over(self, context):
        self._read_event('salmonrun_game_over')

    def on_salmonrun_norma_reached(self, context):
        self._read_event('salmonrun_norma_reached')

    def on_salmonrun_player_dead(self, context, params):
        self._read_event('salmonrun_player_dead')

    def on_salmonrun_player_back(self, context, params):
        self._read_event('salmonrun_player_back')

    def on_salmonrun_wave_start(self, context, params):
        data = self._get_message('salmonrun_wave_start')
        data['text'] = data['text'].format(wave=params['wave'])
        self._read(data)

    def on_salmonrun_wave_finish(self, context):
        self._read_event('salmonrun_wave_finish')

    def on_salmonrun_game_start(self, context, params):
        self._read_event('salmonrun_game_start')

    def on_salmonrun_mr_grizz_comment(self, context, params):
        self._read_event('salmonrun_mr_grizz_comment_%s' % params['text_id'])

    def on_salmonrun_result_judge(self, context):
        result = context.get('salmon_run', {}).get('result', 'unknown')
        data = self._get_message('salmonrun_result_judge_%s' % result)
        self._read(data)
