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

import random
import socket
import sys

from ikalog.constants import *
from ikalog.utils import *


class BoyomiClinet(object):
    ''' 棒読みちゃんにコマンドを送信するクラスです
    http://chi.usamimi.info/Program/Application/BouyomiChan/
    '''

    def __init__(self, host='127.0.0.1', port=50001):
        self.host = host
        self.port = port

    def _connect(self):
        self._socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self._socket.connect((self.host, self.port))

    def _close(self):
        self._socket.close()

    def _send(self, data):
        self._socket.send(data)

    def _command(self, command):
        data = bytearray()
        data.append((command >> 0) & 0xFF)
        data.append((command >> 8) & 0xFF)
        self._connect()
        self._send(data)
        self._close()

    def pause(self):
        self._command(16)

    def resume(self):
        self._command(32)

    def skip(self):
        self._command(48)

    def clear(self):
        self._command(64)

    def read(self, message):
        self.talk(-1, -1, -1, 0, message)

    def talk(self, speed, tone, volume, voice, message):
        data = bytearray()
        # command
        data.append(1)
        data.append(0)
        # speed
        data.append((speed >> 0) & 0xFF)
        data.append((speed >> 8) & 0xFF)
        # tone
        data.append((tone >> 0) & 0xFF)
        data.append((tone >> 8) & 0xFF)
        # volume
        data.append((volume >> 0) & 0xFF)
        data.append((volume >> 8) & 0xFF)
        # voice
        data.append((voice >> 0) & 0xFF)
        data.append((voice >> 8) & 0xFF)
        # encode
        data.append(0)
        # length
        message_data = message.encode('utf-8')
        length = len(message_data)
        data.append((length >> 0) & 0xFF)
        data.append((length >> 8) & 0xFF)
        data.append((length >> 16) & 0xFF)
        data.append((length >> 24) & 0xFF)
        self._connect()
        self._send(data)
        self._send(message_data)
        self._close()


class BoyomiDictionary(object):
    _config = {
        'lobby_matching': ['しばらく待ちましょう'],
        'lobby_matched': ['メンバーが揃いました'],
        'start': ['{map}で{rule}が始まります'],
        'go_sign': ['ゲームスタート！'],
        'killed': ['倒した！', 'やったぁ'],
        'dead': ['あああああああ', 'ぎゃああああ', 'うわああああ'],
        'death_reason_identified': ['{reason}で倒された'],
        'finish': ['ゲーム終了！'],
        'individual_result_win': ['勝った！', 'やったぜ'],
        'individual_result_lose': ['負けた！', 'くやしい'],
        'individual_result_unknown': ['よくわからない', 'どういうことだ？'],
        'individual_kill_death': ['{kill}キル{death}デス'],
        'session_end': ['おつかれさまでした'],
    }

    def __init__(self, config):
        for key in self._config.keys():
            if key in config:
                self._config[key] = config[key]

    def text(self, key):
        return random.choice(self._config.get(key, ['']))

    def get_config(self):
        return self._config


class Boyomi(object):
    '''
    棒読みクライアント
    '''
    custom_read = {
        'initialize': '棒読みちゃん読み上げテストです',
        'nzap85': 'エヌザップ85',
        'nzap89': 'エヌザップ89',
        'bamboo14mk1': '14式竹筒銃・こう',
        'liter3k': 'リッター3ケー',
        'liter3k_custom': 'リッター3ケーカスタム',
        'liter3k_scope': '3ケースコープ',
        'liter3k_scope_custom': '3ケースコープカスタム',
        'squiclean_a': 'スクイックリンアルファ',
        'squiclean_b': 'スクイックリンベータ',
        'rapid_elite': 'ラピッドブラスターエリート',
        'unknown': '未知の武器',
    }

    def __init__(self, host='127.0.0.1', port=50001, dictionary={}):
        self._dict = BoyomiDictionary(dictionary)
        self._client = BoyomiClinet(host, port)
        self._read(self.custom_read['initialize'])

    def config_key(self):
        return 'boyomi'

    def set_config(self, config):
        dictionary = config.get(self.config_key(), {})
        self._dict = BoyomiDictionary(dictionary)

    def get_config(self, config):
        boyomi = self._dict.get_config()
        config[self.config_key()] = boyomi
        return config

    def _read(self, message):
        try:
            self._client.read(message)
        except ConnectionRefusedError:
            error = '「{message}」を読み上げることができませんでした'.format(message=message)
            print(error, file=sys.stderr)

    def _text(self, key):
        return self._dict.text(key)

    def _read_text(self, key):
        self._read(self._text(key))

    def on_lobby_matching(self, context):
        self._read_text('lobby_matching')

    def on_lobby_matched(self, context):
        self._read_text('lobby_matched')

    def on_game_start(self, context):
        map_text = IkaUtils.map2text(context['game']['map'])
        rule_text = IkaUtils.rule2text(context['game']['rule'])
        self._read(
            self._text('start').format(map=map_text, rule=rule_text)
        )

    def on_game_go_sign(self, context):
        self._read_text('go_sign')

    def on_game_killed(self, context):
        self._read_text('killed')

    def on_game_dead(self, context):
        self._read_text('dead')

    def on_game_death_reason_identified(self, context):
        reason = context['game']['last_death_reason']
        label = self._death_reason_label(reason)
        self._client.read(
            self._text('death_reason_identified').format(reason=label)
        )

    def _death_reason_label(self, reason):
        if reason in self.custom_read:
            return self.custom_read[reason]
        if reason in weapons:
            return weapons[reason]['ja']
        if reason in sub_weapons:
            return sub_weapons[reason]['ja']
        if reason in special_weapons:
            return special_weapons[reason]['ja']
        return self.custom_read['unknown']

    def on_game_finish(self, context):
        self._read_text('finish')

    def on_game_individual_result(self, context):
        map = IkaUtils.map2text(context['game']['map'])
        rule = IkaUtils.rule2text(context['game']['rule'])
        won = IkaUtils.getWinLoseText(
            context['game']['won'],
            win_text=self._text('individual_result_win'),
            lose_text=self._text('individual_result_lose'),
            unknown_text=self._text('individual_result_unknown')
        )
        self._read(won)
        me = IkaUtils.getMyEntryFromContext(context)
        kill = me['kills']
        death = me['deaths']
        self._read(
            self._text('individual_kill_death').format(kill=kill, death=death)
        )

    def on_game_session_end(self, context):
        self._read_text('session_end')
