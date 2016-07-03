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
from ikalog.utils import *
from .commentator import Commentator

_ = Localization.gettext_translation('boyomi', fallback=True).gettext

# Needed in GUI mode
try:
    import wx
except:
    pass


class BoyomiClient(object):
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


class Boyomi(Commentator):
    '''
    Boyomi-chan client.
    Boyomi-chan is Japnanese speech server.
    '''

    def __init__(self, host='127.0.0.1', port=50001, dictionary={}):
        super(Boyomi, self).__init__(dictionary)
        self._client = BoyomiClient(host, port)
        self._read_event('initialize')

    def config_key(self):
        return 'boyomi'

    def set_config(self, config):
        dictionary = config.get(self.config_key(), {})
        self._dict = BoyomiDictionary(dictionary)

    def get_config(self, config):
        boyomi = self._dict.get_config()
        config[self.config_key()] = boyomi
        return config

    def _do_read(self, message):
        self._client.read(message['text'])

    def initialize_client(self):
        try:
            self._client = BoyomiClient(self._host, int(self._port))
        except:
            IkaUtils.dprint(_('Failed to apply configuration to boyomi client. Review your settings.'))
            self.dprint(traceback.format_exc())
            self._client = None
            return False
        return True

    def apply_ui(self):
        self._enabled = self.check_enable.GetValue()
        self._host = self.edit_host.GetValue()
        self._port = self.edit_port.GetValue()
        self.initialize_client()

    def refresh_ui(self):
        self.check_enable.SetValue(self._enabled)

        if not self._host is None:
            self.edit_host.SetValue(self._host)
        else:
            self.edit_host.SetValue('')

        if not self._port is None:
            self.edit_port.SetValue(str(self._port))
        else:
            self.edit_port.SetValue('50001')

        self._internal_update = False

    def on_config_reset(self, context=None):
        self._enabled = False
        self._host = '127.0.0.1'
        self._port = '50001'

    def on_config_load_from_context(self, context):
        self.on_config_reset(context)

        try:
            conf = context['config']['boyomi']
        except:
            conf = {}

        if 'Enable' in conf:
            self._enabled = conf['Enable']

        if 'host' in conf:
            self._host = conf['host']

        if 'port' in conf:
            try:
                self._port = int(conf['port'])
            except ValueError:
                IkaUtils.dprint('%s: port must be an integer' % self)
                self._port = 50001

        self.refresh_ui()
        self.initialize_client()
        return True

    def on_config_save_to_context(self, context):
        context['config']['boyomi'] = {
            'Enable': self._enabled,
            'host': self._host,
            'port': self._port,
        }

    def on_config_apply(self, context):
        self.apply_ui()

    def on_test_button_click(self, event):
        self._read_event('initialize')

    def on_option_tab_create(self, notebook):
        self.panel = wx.Panel(notebook, wx.ID_ANY)
        self.panel_name = _('Boyomi')
        self.layout = wx.BoxSizer(wx.VERTICAL)

        self.check_enable = wx.CheckBox(
            self.panel, wx.ID_ANY, _('Enable Boyomi client'))
        self.edit_host = wx.TextCtrl(self.panel, wx.ID_ANY, 'host')
        self.edit_port = wx.TextCtrl(self.panel, wx.ID_ANY, 'port')
        self.button_test = wx.Button(self.panel, wx.ID_ANY, _('Test intergration'))

        try:
            layout = wx.GridSizer(2, 4)
        except:
            layout = wx.GridSizer(2)

        layout.Add(wx.StaticText(self.panel, wx.ID_ANY, _('host')))
        layout.Add(self.edit_host)
        layout.Add(wx.StaticText(self.panel, wx.ID_ANY, _('port')))
        layout.Add(self.edit_port)

        self.layout.Add(self.check_enable)
        self.layout.Add(layout, flag=wx.EXPAND)
        self.layout.Add(self.button_test)

        self.panel.SetSizer(self.layout)

        self.button_test.Bind(wx.EVT_BUTTON, self.on_test_button_click)
