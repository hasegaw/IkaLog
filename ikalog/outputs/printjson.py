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
import os
from datetime import datetime
import time
import json

from ikalog.utils import *


# Needed in GUI mode
try:
    import wx
except:
    pass

# IkaOutput_JSON: IkaLog Output Plugin for JSON Logging
#
# Write JSON Log file


class JSON(object):

    def apply_ui(self):
        self.enabled = self.checkEnable.GetValue()
        self.json_filename = self.editJsonFilename.GetValue()

    def refresh_ui(self):
        self._internal_update = True
        self.checkEnable.SetValue(self.enabled)

        if not self.json_filename is None:
            self.editJsonFilename.SetValue(self.json_filename)
        else:
            self.editJsonFilename.SetValue('')

    def on_config_reset(self, context=None):
        self.enabled = False
        self.json_filename = os.path.join(os.getcwd(), 'ika.json')

    def on_config_load_from_context(self, context):
        self.on_config_reset(context)
        try:
            conf = context['config']['json']
        except:
            conf = {}

        if 'Enable' in conf:
            self.enabled = conf['Enable']

        if 'JsonFilename' in conf:
            self.json_filename = conf['JsonFilename']

        self.refresh_ui()
        return True

    def on_config_save_to_context(self, context):
        context['config']['json'] = {
            'Enable': self.enabled,
            'JsonFilename': self.json_filename,
        }

    def on_config_apply(self, context):
        self.apply_ui()

    def on_option_tab_create(self, notebook):
        self.panel = wx.Panel(notebook, wx.ID_ANY)
        self.page = notebook.InsertPage(0, self.panel, 'JSON')
        self.layout = wx.BoxSizer(wx.VERTICAL)
        self.panel.SetSizer(self.layout)
        self.checkEnable = wx.CheckBox(
            self.panel, wx.ID_ANY, u'JSONファイルへ戦績を出力する')
        self.editJsonFilename = wx.TextCtrl(self.panel, wx.ID_ANY, u'hoge')

        self.layout.Add(wx.StaticText(self.panel, wx.ID_ANY, u'JSON保存先ファイル'))
        self.layout.Add(self.editJsonFilename, flag=wx.EXPAND)

        self.layout.Add(self.checkEnable)

    ##
    # Write a line to text file.
    # @param self     The Object Pointer.
    # @param record   Record (text)
    #
    def write_record(self, record):
        try:
            json_file = open(self.json_filename, "a")
            json_file.write(record)
            json_file.close
        except:
            print("JSON: Failed to write JSON file")

    ##
    # Generate a record
    # @param self      The Object Pointer.
    # @param context   IkaLog context
    #
    def get_record_game_result(self, context):
        map = IkaUtils.map2text(context['game']['map'])
        rule = IkaUtils.rule2text(context['game']['rule'])
        won = IkaUtils.getWinLoseText(
            context['game']['won'], win_text="win", lose_text="lose", unknown_text="unknown")

        t = datetime.now()
        t_str = t.strftime("%Y,%m,%d,%H,%M")
        t_unix = int(time.mktime(t.timetuple()))

        record = {
            'time': t_unix,
            'event': 'GameResult',
            'map': map,
            'rule': rule,
            'result': won
        }

        # ウデマエ
        try:
            udemae = context['scenes']['result_udemae']
            record['udemae_pre'] = result_udemae['udemae_exp_pre']
            record['udemae_exp_pre'] = udemae['udemae_exp_pre']
            record['udemae_after'] = udemae['udemae_str_after']
            record['udemae_exp_after'] = udemae['udemae_exp_after']
        except:
            pass

        # オカネ
        try:
            record['cash_after'] = context['scenes']['result_gears']['cash']
        except:
            pass

        # 個人成績
        me = IkaUtils.getMyEntryFromContext(context)

        for field in ['team', 'kills', 'deaths', 'score', 'udemae_pre', 'weapon', 'rank_in_team']:
            if field in me:
                record[field] = me[field]

        # 全プレイヤーの成績
        record['players'] = []
        for player in context['game']['players']:
            player_record = {}
            for field in ['team', 'kills', 'deaths', 'score', 'udemae_pre', 'weapon', 'rank_in_team']:
                if field in player:
                    player_record[field] = player[field]
            record['players'].append(player_record)

        return json.dumps(record, separators=(',', ':')) + "\n"

    ##
    # on_game_individual_result Hook
    # @param self      The Object Pointer
    # @param context   IkaLog context
    #
    def on_game_session_end(self, context):
        IkaUtils.dprint('%s (enabled = %s)' % (self, self.enabled))

        if not self.enabled:
            return

        record = self.get_record_game_result(context)
        self.write_record(record)

    ##
    # Constructor
    # @param self          The Object Pointer.
    # @param json_filename JSON log file name
    #
    def __init__(self, json_filename=None):
        self.enabled = (not json_filename is None)
        self.json_filename = json_filename
