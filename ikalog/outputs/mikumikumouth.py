#!/usr/bin/env python3
# -*- coding: utf-8 -*-
#
#  IkaLog
#  ======
#  Copyright (C) 2015 ExceptionError
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
import random
import select
import socket
import sys
import traceback
import threading

from ikalog.constants import *
from ikalog.utils import *


class MikuMikuMouthServer(object):
    ''' みくみくまうすにコマンドを送信するサーバーです
    http://mikumikumouth.net/
    '''

    def __init__(self, host='127.0.0.1', port=50082):
        self.host = host
        self.port = port
        self._socks = set([])

    def listen(self):
        self._listen_thread = threading.Thread(target=self._listen)
        self._listen_thread.start()

    def _listen(self):
        self._server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self._socks.add(self._server)
        try:
            self._server.bind((self.host, self.port))
            self._server.listen(5)
            self._loop = True
            while self._loop:
                rready, wready, xready = select.select(self._socks, [], [], 1)
                for sock in rready:
                    if sock is self._server:
                        conn, address = self._server.accept()
                        self._socks.add(conn)
        finally:
            for sock in self._socks:
                sock.close()
            self._socks.clear()

    def close(self):
        self._loop = False

    def _send(self, text):
        for sock in self._socks:
            if sock is not self._server:
                try:
                    sock.sendall(text.encode('utf-8'))
                except ConnectionAbortedError:
                    pass

    def talk(self, data):
        print(json.dumps(data))
        self._send(json.dumps(data))


class MikuMikuMouthDictionaly(object):
    '''
    みくみくまうす辞書
    '''
    _config = {
        'lobby_matching': [
            {'text': 'しばらく待ちましょう', 'emotion': 'response', 'tag': 'white'},
        ],
        'lobby_matched': [
            {'text': 'メンバーが揃いました', 'emotion': 'hakushu', 'tag': 'white'},
        ],
        'start': [
            {
                'text': '{map}で{rule}が始まります',
                'emotion': 'greeting',
                'tag': 'white'
            },
        ],
        'go_sign': [
            {'text': 'ゲームスタート！', 'emotion': 'meirei', 'tag': 'white'},
        ],
        'killed': [
            {'text': '倒した！', 'emotion': 'warai', 'tag': 'white'},
            {'text': 'やったぁ', 'emotion': 'wktk', 'tag': 'white'},
        ],
        'dead': [
            {'text': 'ぎゃあああああ', 'emotion': 'no', 'tag': 'white'},
            {'text': 'あああああああ', 'emotion': 'cry', 'tag': 'white'},
            {'text': 'うわあああああ', 'emotion': 'bikkuri', 'tag': 'white'},
        ],
        'death_reason_identified': [
            {'text': '{reason}で倒された', 'emotion': 'none', 'tag': 'white'}
        ],
        'finish': [
            {'text': 'ゲーム終了！', 'emotion': 'greeting', 'tag': 'white'},
        ],
        'individual_result_win': [
            {'text': '勝った！', 'emotion': 'happy', 'tag': 'white'},
            {'text': 'やったぁ', 'emotion': 'shy', 'tag': 'white'},
        ],
        'individual_result_lose': [
            {'text': '負けた！', 'emotion': 'no', 'tag': 'white'},
            {'text': 'くやしい', 'emotion': 'cry', 'tag': 'white'},
        ],
        'individual_result_unknown': [
            {'text': 'よくわからない', 'emotion': 'question', 'tag': 'white'},
            {'text': 'どういうこと？', 'emotion': 'tsukkomi', 'tag': 'white'},
        ],
        'individual_kill_death': [
            {'text': '{kill}キル{death}デス', 'emotion': 'none', 'tag': 'white'},
        ],
        'session_end': [
            {'text': 'おつかれさまでした', 'emotion': 'byebye', 'tag': 'white'},
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


class MikuMikuMouth(object):
    '''
    みくみくまうすサーバー
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

    def __init__(self, host='127.0.0.1', port=50082, dictionary={}):
        self._enabled = True
        self._dict = MikuMikuMouthDictionaly(dictionary)
        self._server = MikuMikuMouthServer(host, port)
        self._server.listen()
        self._read(self.custom_read['initialize'])

    def config_key(self):
        return 'mikumikumouth'

    def set_config(self, config):
        dictionary = config.get(self.config_key(), {})
        self._dict = BoyomiDictionary(dictionary)

    def get_config(self, config):
        mikumikumouth = self._dict.get_config()
        config[self.config_key()] = mikumikumouth
        return config

    def _read(self, message):
        if (self._server is None) or (not self._enabled):
            return

        try:
            self._server.talk(message)
        except ConnectionRefusedError:
            error = '「{message}」を読み上げることができませんでした'.format(message=message)
            IkaUtils.dprint(error)

    def _text(self, key):
        return self._dict.data(key)

    def _read_text(self, key):
        self._read(self._text(key))

    def on_stop(self, context):
        self._server.close()

    def on_lobby_matching(self, context):
        self._read_text('lobby_matching')

    def on_lobby_matched(self, context):
        self._read_text('lobby_matched')

    def on_game_start(self, context):
        map_text = IkaUtils.map2text(context['game']['map'], unknown='スプラトゥーン')
        rule_text = IkaUtils.rule2text(context['game']['rule'], unknown='ゲーム')
        data = self._text('start')
        data['text'] = data['text'].format(map=map_text, rule=rule_text)
        self._read(data)

    def on_game_go_sign(self, context):
        self._read_text('go_sign')

    def on_game_killed(self, context):
        self._read_text('killed')

    def on_game_dead(self, context):
        self._read_text('dead')

    def on_game_death_reason_identified(self, context):
        reason = context['game']['last_death_reason']
        label = self._death_reason_label(reason)
        data = self._text('death_reason_identified')
        data['text'] = data['text'].format(reason=label)
        self._read(data)

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
        data = self._text('individual_kill_death')
        data['text'] = data['text'].format(kill=kill, death=death)
        self._read(data)

    def on_game_session_end(self, context):
        self._read_text('session_end')
