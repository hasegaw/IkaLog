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

from ikalog.constants import *
from ikalog.utils import *

class CommentatorDictionary(object):
    '''
    実況アプリ用辞書

    emotionは適当に決めてください:
    http://mikumikumouth.net/developer.html#emotion一覧
    '''
    _config = {
        'initialize': [
            {'text': '読み上げテストです', 'emotion': 'salute'},
        ],
        'lobby_matching': [
            {'text': 'しばらく待ちましょう', 'emotion': 'response'},
        ],
        'lobby_matched': [
            {'text': 'メンバーが揃いました', 'emotion': 'hakushu'},
        ],
        'start': [
            {
                'text': '{map}で{rule}が始まります',
                'emotion': 'greeting',
            },
        ],
        'go_sign': [
            {'text': 'ゲームスタート！', 'emotion': 'meirei'},
        ],
        'killed': [
            {'text': '倒した！', 'emotion': 'warai'},
            {'text': 'やったぁ', 'emotion': 'wktk'},
        ],
        'dead': [
            {'text': 'ぎゃあああああ', 'emotion': 'no'},
            {'text': 'あああああああ', 'emotion': 'cry'},
            {'text': 'うわあああああ', 'emotion': 'bikkuri'},
        ],
        'death_reason_identified': [
            {'text': '{reason}で倒された', 'emotion': 'none'}
        ],
        'death_reason_oob': [
            {'text': '場外に落ちた', 'emotion': 'bikkuri'},
        ],
        'finish': [
            {'text': 'ゲーム終了！', 'emotion': 'greeting'},
        ],
        'individual_result_win': [
            {'text': '勝った！', 'emotion': 'happy'},
            {'text': 'やったぁ', 'emotion': 'shy'},
        ],
        'individual_result_lose': [
            {'text': '負けた！', 'emotion': 'no'},
            {'text': 'くやしい', 'emotion': 'cry'},
        ],
        'individual_result_unknown': [
            {'text': 'よくわからない', 'emotion': 'question'},
            {'text': 'どういうこと？', 'emotion': 'tsukkomi'},
        ],
        'individual_kill_death': [
            {'text': '{kill}キル{death}デス', 'emotion': 'none'},
        ],
        'session_end': [
            {'text': 'おつかれさまでした', 'emotion': 'byebye'},
        ],
        'session_abort': [
            {'text': 'ゲームを見失いました', 'emotion': 'byebye'},
        ],
        'ranked_we_lead': [
            {'text': 'カウントリードした', 'emotion': 'hakushu'},
            {'text': 'このまま行けば勝てるぞ', 'emotion': 'wktk'},
        ],
        'ranked_they_lead': [
            {'text': 'カウントリードされた', 'emotion': 'cry'},
            {'text': 'このままでは負けるぞ', 'emotion': 'no'},
        ],
        'splatzone_we_got': [
            {'text': 'エリア確保した', 'emotion': 'hakushu'},
            {'text': 'エリア確保！', 'emotion': 'wktk'},
        ],
        'splatzone_we_lost': [
            {'text': 'カウントストップされた', 'emotion': 'bikkuri'},
            {'text': 'エリアを失った', 'emotion': 'notsay'},
        ],
        'splatzone_they_got': [
            {'text': 'エリア確保された', 'emotion': 'bikkuri'},
            {'text': 'エリアを取られた', 'emotion': 'notsay'},
        ],
        'splatzone_they_lost': [
            {'text': 'カウントストップした', 'emotion': 'warai'},
            {'text': '食い止めた！', 'emotion': 'happy'},
        ],
        'tower_we_got': [
            {'text': 'ヤグラゲット', 'emotion': 'hakushu'},
            {'text': 'ヤグラわ我らのもの', 'emotion': 'response'},
            {'text': 'ソイヤ！', 'emotion': 'wktk'},
        ],
        'tower_we_lost': [
            {'text': 'ヤグラがやられた', 'emotion': 'bikkuri'},
            {'text': 'ヤグラを失った', 'emotion': 'notsay'},
        ],
        'tower_they_got': [
            {'text': 'ヤグラをとられた', 'emotion': 'cry'},
        ],
        'tower_they_lost': [
            {'text': 'ヤグラをとめた', 'emotion': 'hakushu'},
            {'text': 'ヤグラをストップした', 'emotion': 'warai'},
            {'text': '食い止めた！', 'emotion': 'happy'},
        ],
        'rainmaker_we_got': [
            {'text': 'ほこゲット', 'emotion': 'hakushu'},
            {'text': 'ホコわ我らのもの', 'emotion': 'wktk'},
        ],
        'rainmaker_we_lost': [
            {'text': 'ホコがやられた', 'emotion': 'bikkuri'},
            {'text': 'ホコを失った', 'emotion': 'notsay'},
        ],
        'rainmaker_they_got': [
            {'text': 'ホコをとられた', 'emotion': 'cry'},
        ],
        'rainmaker_they_lost': [
            {'text': 'ホコをとめた', 'emotion': 'hakushu'},
            {'text': 'ホコをストップした', 'emotion': 'warai'},
            {'text': '食い止めた！', 'emotion': 'happy'},
        ],
    }

    def __init__(self, config):
        for key in self._config.keys():
            if key in config:
                self._config[key] = config[key]

    def data(self, key):
        return random.choice(self._config.get(key, [''])).copy()

    def get_config(self):
        return self._config


class Commentator(object):
    '''
    実況者基底クラス
    '''
    custom_read = {
        '52gal': 'ごーにーガロン',
        '52gal_deco': 'ごーにーガロンデコ',
        '96gal': 'きゅーろくガロン',
        '96gal_deco': 'きゅーろくガロンデコ',
        'nzap85': 'エヌザップ85',
        'nzap89': 'エヌザップ89',
        'bamboo14mk1': 'ひとよん式竹筒じゅう・こう',
        'bamboo14mk2': 'ひとよん式竹筒じゅう・おつ',
        'bamboo14mk3': 'ひとよん式竹筒じゅう・へい',
        'liter3k': 'リッター3ケー',
        'liter3k_custom': 'リッター3ケーカスタム',
        'liter3k_scope': '3ケースコープ',
        'liter3k_scope_custom': '3ケースコープカスタム',
        'promodeler_rg': 'プロモデラーアールジー',
        'promodeler_mg': 'プロモデラーエムジー',
        'squiclean_a': 'スクイックリンアルファ',
        'squiclean_b': 'スクイックリンベータ',
        'squiclean_g': 'スクイックリンガンマ',
        'rapid_elite': 'ラピッドブラスターエリート',
        'rapid_elite_deco': 'ラピッドブラスターエリートデコ',
        'unknown': '未知の武器',
    }

    def __init__(self, dictionary={}):
        self._enabled = True
        self._dict = CommentatorDictionary(dictionary)

    def set_config(self, config):
        dictionary = config.get(self.config_key(), {})
        self._dict = CommentatorDictionary(dictionary)

    def get_config(self, config):
        commentator = self._dict.get_config()
        config[self.config_key()] = commentator
        return config

    def _read(self, message):
        if (not self._enabled):
            return

        try:
            self._do_read(message)
        except ConnectionRefusedError:
            error = '「{message}」を読み上げることができませんでした'.format(message=message['text'])
            IkaUtils.dprint(error)

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
        map_text = IkaUtils.map2text(context['game']['map'], unknown='スプラトゥーン')
        rule_text = IkaUtils.rule2text(context['game']['rule'], unknown='ゲーム')
        data = self._get_message('start')
        data['text'] = data['text'].format(map=map_text, rule=rule_text)
        self._read(data)

    def on_game_go_sign(self, context):
        self._read_event('go_sign')

    def on_game_killed(self, context):
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
        data['text'] = data['text'].format(kill=kill, death=death)
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
