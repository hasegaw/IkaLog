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
from ikalog.plugin import IkaLogPlugin
from ikalog.utils import *
from ikalog.outputs.commentator import Commentator


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
        for sock in self._socks.copy():
            if sock is not self._server:
                close_sock = False

                try:
                    sock.sendall(text.encode('utf-8'))
                except ConnectionAbortedError:
                    close_sock = True

                except BrokenPipeError:
                    close_sock = True

                if close_sock:
                    self._socks.remove(sock)
                    sock.close()

    def talk(self, data):
        print(json.dumps(data))
        self._send(json.dumps(data))


class MikuMikuMouthPlugin(Commentator, IkaLogPlugin):
    '''
    みくみくまうすサーバー
    '''

    plugin_name = 'MikuMikuMouth'

    def __init__(self):
        self._server = None
        super(MikuMikuMouthPlugin, self).__init__()
        super(Commentator, self).__init__()

    def on_validate_configuration(self, config):
        assert config['enabled'] in [True, False]
        assert int(config['port']) > 0
        return True

    def on_reset_configuration(self):
        self.config['enabled'] = False
        self.config['host'] = 'localhost'
        self.config['port'] = 50082

    def on_set_configuration(self, config):
        self.config['host'] = config['host']
        self.config['port'] = config['port']
        self.config['enabled'] = config['enabled']

        if self._server is not None:
            self._server.close()

        if not self.config['enabled']:
            self._server = None
        else:
            self._server = MikuMikuMouthServer(
                self.config['host'],
                self.config['port']
            )
            self._server.listen()

    def _do_read(self, message):
        if self._server is None:
            return

        message['tag'] = 'white'
        self._server.talk(message)

    def on_stop(self, context):
        self._server.close()


class LegacyMikuMikuMouth(MikuMikuMouthPlugin):

    def __init__(self,
                 host='127.0.0.1',
                 port=50082,
                 dictionary={},
                 dictionary_csv=None,
                 custom_read_csv=None):

        super(LegacyMikuMikuMouth, self).__init__()


MikuMikuMouth = LegacyMikuMikuMouth
