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

import random
import socket
import sys
import traceback


from ikalog.constants import *
from ikalog.outputs.commentator import Commentator
from ikalog.plugin import IkaLogPlugin
from ikalog.utils import *

_ = Localization.gettext_translation('boyomi', fallback=True).gettext


class BoyomiClient(object):
    '''
    棒読みちゃんにコマンドを送信するクラスです
    http://chi.usamimi.info/Program/Application/BouyomiChan/

    FIXME: 非同期で動いてほしい（通信中に IkaEngine が止まるので）
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


class BoyomiPlugin(Commentator, IkaLogPlugin):
    '''
    Boyomi-chan client.
    Boyomi-chan is Japnanese speech server.
    '''

    plugin_name = 'Boyomi'

    def __init__(self):
        self._client = None
        super(BoyomiPlugin, self).__init__()
        super(Commentator, self).__init__()

    def on_validate_configuration(self, config):
        assert config['enabled'] in [True, False]
        return True

    def on_reset_configuration(self):
        self.config['enabled'] = False
        self.config['host'] = 'localhost'
        self.config['port'] = 50001

    def on_set_configuration(self, config):
        self.config['host'] = config['host']
        self.config['port'] = config['port']
        self.config['enabled'] = config['enabled']

        modified = False
        client = self._client
        if client is not None:
            host_changed = (client.host != self.config['host'])
            port_changed = (client.host != self.config['port'])
            modified = host_changed or port_changed

        if modified:
            self._client = BoyomiClient(self._host, int(self._port))

        # FIXME: load custom read

    def _do_read(self, message):
        if self._client is None:
            return

        self._client.read(message['text'])


class LegacyBoyomi(BoyomiPlugin):

    def __init__(self, host='127.0.0.1', port=50001, dictionary={}, dictionary_csv=None, custom_read_csv=None):
        super(LegacyBoyomi, self).__init__()

        config = {
            'enabled': True,
            'host': host,
            'port': port,
            'dictionary': dictionary,
            'dictionary_csv': dictionary_csv,
            'custom_read_csv': custom_read_csv,
        }

        if config['enabled']:
            self.set_configuration(config)

Boyomi = LegacyBoyomi
