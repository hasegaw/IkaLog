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
from .commentator import Commentator

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


class MikuMikuMouth(Commentator):
    '''
    みくみくまうすサーバー
    '''
    def __init__(self, host='127.0.0.1', port=50082, dictionary={}):
        super(MikuMikuMouth, self).__init__(dictionary)
        self._server = MikuMikuMouthServer(host, port)
        self._server.listen()
        self._read_event('initialize');

    def config_key(self):
        return 'mikumikumouth'

    def set_config(self, config):
        dictionary = config.get(self.config_key(), {})
        self._dict = BoyomiDictionary(dictionary)

    def get_config(self, config):
        mikumikumouth = self._dict.get_config()
        config[self.config_key()] = mikumikumouth
        return config

    def _do_read(self, message):
        if (self._server is None) or (not self._enabled):
            return

        message["tag"] = "white"
        self._server.talk(message)
