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

import json
import os
import time

from ikalog.utils import *

_ = Localization.gettext_translation('json', fallback=True).gettext

# Needed in GUI mode
try:
    import wx
except:
    pass


def _set(dest, dest_key, src, src_key):
    if src_key not in src:
        return
    dest[dest_key] = src[src_key]

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
        self.panel_name = _('JSON')
        self.layout = wx.BoxSizer(wx.VERTICAL)
        self.panel.SetSizer(self.layout)
        self.checkEnable = wx.CheckBox(
            self.panel, wx.ID_ANY, _('Enable JSON Log'))
        self.editJsonFilename = wx.TextCtrl(self.panel, wx.ID_ANY, u'hoge')

        self.layout.Add(wx.StaticText(self.panel, wx.ID_ANY, _('Log Filename')))
        self.layout.Add(self.editJsonFilename, flag=wx.EXPAND)

        self.layout.Add(self.checkEnable)

    def _open_game_session(self, context):
        self._called_close_game_session = False

    def on_game_go_sign(self, context):
        self._open_game_session(context)

    def on_game_start(self, context):
        # Fallback in the case on_game_go_sign was skipped.
        self._open_game_session(context)

    ##
    # Write a line to text file.
    # @param self     The Object Pointer.
    # @param record   Record (text)
    # @param context  The context
    #
    def write_record(self, record, context):
        try:
            if self.append_data:
                json_file = open(self.json_filename, "a")
            else:
                filename = IkaUtils.get_file_name(self.json_filename, context)
                json_file = open(filename, 'w')
            json_file.write(json.dumps(record, separators=(',', ':')) + '\n')
            json_file.close()
        except:
            print("JSON: Failed to write JSON file")

    ##
    # Generate a record
    # @param self      The Object Pointer.
    # @param context   IkaLog context
    #
    def get_record_game_result(self, context):
        map = context['game']['map']
        rule = context['game']['rule']
        won = IkaUtils.getWinLoseText(
            context['game']['won'], win_text="win", lose_text="lose", unknown_text="unknown")
        t_unix = int(IkaUtils.get_end_time(context).timestamp())

        record = {
            'time': t_unix,
            'event': 'GameResult',
            'map': map,
            'rule': rule,
            'result': won
        }

        _set(record, 'lobby', context['lobby'], 'type')
        if (not record.get('lobby')) and context['game'].get('is_fes'):
            record['lobby'] = 'festa'

        # ウデマエ
        _set(record, 'udemae_pre', context['game'], 'result_udemae_str_pre')
        _set(record, 'udemae_exp_pre', context['game'], 'result_udemae_exp_pre')
        _set(record, 'udemae_after', context['game'],'result_udemae_str')
        _set(record, 'udemae_exp_after', context['game'], 'result_udemae_exp')

        # オカネ
        if context['scenes'].get('result_gears'):
            _set(record, 'cash_after',
                 context['scenes']['result_gears'], 'cash')

        # 個人成績
        me = IkaUtils.getMyEntryFromContext(context)
        if me:
            for field in ['team', 'kills', 'deaths', 'score', 'weapon',
                          'rank_in_team']:
                _set(record, field, me, field)

        # 全プレイヤーの成績
        if context['game'].get('players'):
            record['players'] = []
            for player in context['game']['players']:
                player_record = {}
                for field in ['team', 'kills', 'deaths', 'score', 'weapon',
                              'rank_in_team']:
                    _set(player_record, field, player, field)
                record['players'].append(player_record)

        return record

    def _close_game_session(self, context):
        if self._called_close_game_session:
            return
        self._called_close_game_session = True

        IkaUtils.dprint('%s (enabled = %s)' % (self, self.enabled))
        if not self.enabled:
            return

        record = self.get_record_game_result(context)
        self.write_record(record, context)

    ##
    # on_game_individual_result Hook
    # @param self      The Object Pointer
    # @param context   IkaLog context
    #
    def on_game_session_end(self, context):
        self._close_game_session(context)

    def on_game_session_abort(self, context):
        self._close_game_session(context)

    ##
    # Constructor
    # @param self          The Object Pointer.
    # @param json_filename JSON log file name
    # @param append_data whether append or overwrite the data to file.
    #
    def __init__(self, json_filename=None, append_data=True):
        self.enabled = (not json_filename is None)
        self.json_filename = json_filename
        self.append_data = append_data

        # If true, it means the data is not saved.
        self._called_close_game_session = False
