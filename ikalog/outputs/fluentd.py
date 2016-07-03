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

from ikalog.utils import *

# Needed in GUI mode
try:
    import wx
except:
    pass

# IkaOutput_Fluentd: IkaLog Output Plugin for Fluentd ecosystem
#


class Fluentd(object):

    def apply_ui(self):
        self.enabled = self.checkEnable.GetValue()
        self.host = self.editHost.GetValue()
        self.port = self.editPort.GetValue()
        self.tag = self.editTag.GetValue()
        self.username = self.editUsername.GetValue()

    def refresh_ui(self):
        self._internal_update = True
        self.checkEnable.SetValue(self.enabled)

        if not self.host is None:
            self.editHost.SetValue(self.host)
        else:
            self.editHost.SetValue('')

        if not self.port is None:
            self.editPort.SetValue(self.port)
        else:
            self.editPort.SetValue('')

        if not self.tag is None:
            self.editTag.SetValue(self.tag)
        else:
            self.editTag.SetValue('')

        if not self.username is None:
            self.editUsername.SetValue(self.username)
        else:
            self.editUsername.SetValue('')

    def on_config_reset(self, context=None):
        self.enabled = False
        self.host = ''
        self.port = ''
        self.tag = ''
        self.username = ''

    def on_config_load_from_context(self, context):
        self.on_config_reset(context)
        try:
            conf = context['config']['fluentd']
        except:
            conf = {}

        if 'Enable' in conf:
            self.enabled = conf['Enable']

        if 'Host' in conf:
            self.host = conf['Host']

        if 'Port' in conf:
            self.port = conf['Port']

        if 'Tag' in conf:
            self.tag = conf['Tag']

        if 'Username' in conf:
            self.username = conf['Username']

        self.refresh_ui()
        return True

    def on_config_save_to_context(self, context):
        context['config']['fluentd'] = {
            'Enable': self.enabled,
            'Host': self.host,
            'Port': self.port,
            'Username': self.username,
        }

    def on_config_apply(self, context):
        self.apply_ui()

    def on_option_tab_create(self, notebook):
        self.panel = wx.Panel(notebook, wx.ID_ANY, size=(640, 360))
        self.panel_name = 'Fluentd'
        self.layout = wx.BoxSizer(wx.VERTICAL)

        self.checkEnable = wx.CheckBox(
            self.panel, wx.ID_ANY, u'Fluentd へ戦績を送信する')
        self.editHost = wx.TextCtrl(self.panel, wx.ID_ANY, u'hoge')
        self.editPort = wx.TextCtrl(self.panel, wx.ID_ANY, u'hoge')
        self.editTag = wx.TextCtrl(self.panel, wx.ID_ANY, u'hoge')
        self.editUsername = wx.TextCtrl(self.panel, wx.ID_ANY, u'hoge')

        try:
            layout = wx.GridSizer(2, 4)
        except:
            layout = wx.GridSizer(2)

        layout.Add(wx.StaticText(self.panel, wx.ID_ANY, u'ホスト'))
        layout.Add(self.editHost)
        layout.Add(wx.StaticText(self.panel, wx.ID_ANY, u'ポート'))
        layout.Add(self.editPort)
        layout.Add(wx.StaticText(self.panel, wx.ID_ANY, u'タグ'))
        layout.Add(self.editTag)
        layout.Add(wx.StaticText(self.panel, wx.ID_ANY, u'ユーザ名'))
        layout.Add(self.editUsername)

        self.layout.Add(self.checkEnable)
        self.layout.Add(layout)

        self.panel.SetSizer(self.layout)

    ##
    # Log a record to Fluentd.
    # @param self       The Object Pointer.
    # @param recordType Record Type (tag)
    # @param record     Record
    #
    def submit_record(self, recordType, record):
        try:
            from fluent import sender
            from fluent import event
            if self.host is None:
                sender = sender.setup(self.tag)
            else:
                sender.setup(self.tag, host=self.host, port=self.port)

            event.Event(recordType, record)
        except:
            print("Fluentd: Failed to submit a record")

    ##
    # Generate a record for on_game_individual_result.
    # @param self      The Object Pointer.
    # @param context   IkaLog context
    #
    def get_record_game_individual_result(self, context):
        map = IkaUtils.map2text(context['game']['map'])
        rule = IkaUtils.rule2text(context['game']['rule'])
        won = IkaUtils.getWinLoseText(
            context['game']['won'], win_text="win", lose_text="lose", unknown_text="unknown")
        return {
            'username': self.username,
            'map': map,
            'rule': rule,
            'result': won
        }

    ##
    # on_game_individual_result Hook
    # @param self      The Object Pointer
    # @param context   IkaLog context
    #
    def on_game_individual_result(self, context):
        IkaUtils.dprint('%s (enabled = %s)' % (self, self.enabled))

        if not self.enabled:
            return

        record = self.get_record_game_individual_result(context)
        self.submit_record('gameresult', record)

    ##
    # Check availability of modules this plugin depends on.
    # @param self      The Object Pointer.
    #
    def check_import(self):
        try:
            from fluent import sender
            from fluent import event
        except:
            print("モジュール fluent-logger がロードできませんでした。 Fluentd 連携ができません。")
            print("インストールするには以下のコマンドを利用してください。\n    pip install fluent-logger\n")

    ##
    # Constructor
    # @param self     The Object Pointer.
    # @param tag      tag
    # @param username Username of the player.
    # @param host     Fluentd host if Fluentd is on a different node
    # @param port     Fluentd port
    # @param username Name the bot use on Slack
    #
    def __init__(self, tag='ikalog', username='ika', host=None, port=24224):
        self.enabled = False
        self.tag = tag
        self.username = username
        self.host = host
        self.port = port

        self.check_import()

if __name__ == "__main__":
    obj = Fluentd()
