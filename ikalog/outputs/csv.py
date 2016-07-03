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
import time

from ikalog.utils import *

_ = Localization.gettext_translation('csv', fallback=True).gettext

# Needed in GUI mode
try:
    import wx
except:
    pass

# @package IkaOutput_CSV

# IkaOutput_CSV: IkaLog CSV Output Plugin
#
# Log Splatoon game results as CSV format.


class CSV(object):

    def apply_ui(self):
        self.enabled = self.checkEnable.GetValue()
        self.csv_filename = self.editCsvFilename.GetValue()

    def refresh_ui(self):
        self._internal_update = True
        self.checkEnable.SetValue(self.enabled)

        if not self.csv_filename is None:
            self.editCsvFilename.SetValue(self.csv_filename)
        else:
            self.editCsvFilename.SetValue('')

    def on_config_reset(self, context=None):
        self.enabled = False
        self.csv_filename = os.path.join(os.getcwd(), 'ika.csv')

    def on_config_load_from_context(self, context):
        self.on_config_reset(context)
        try:
            conf = context['config']['csv']
        except:
            conf = {}

        if 'Enable' in conf:
            self.enabled = conf['Enable']

        if 'CsvFilename' in conf:
            self.csv_filename = conf['CsvFilename']

        self.refresh_ui()
        return True

    def on_config_save_to_context(self, context):
        context['config']['csv'] = {
            'Enable': self.enabled,
            'CsvFilename': self.csv_filename,
        }

    def on_config_apply(self, context):
        self.apply_ui()

    def on_option_tab_create(self, notebook):
        self.panel = wx.Panel(notebook, wx.ID_ANY)
        self.panel_name = _('CSV')
        self.layout = wx.BoxSizer(wx.VERTICAL)
        self.panel.SetSizer(self.layout)
        self.checkEnable = wx.CheckBox(
            self.panel, wx.ID_ANY, _('Enable CSV Log'))
        self.editCsvFilename = wx.TextCtrl(self.panel, wx.ID_ANY, u'hoge')

        self.layout.Add(wx.StaticText(self.panel, wx.ID_ANY, _('Log Filename')))
        self.layout.Add(self.editCsvFilename, flag=wx.EXPAND)

        self.layout.Add(self.checkEnable)

    ##
    # Write a line to text file.
    # @param self     The Object Pointer.
    # @param record   Record (text)
    #
    def write_record(self, record):
        try:
            csv_file = open(self.csv_filename, "a")
            csv_file.write(record)
            csv_file.close
        except:
            print("CSV: Failed to write CSV File")

    ##
    # Generate a message for on_game_individual_result.
    # @param self      The Object Pointer.
    # @param context   IkaLog context
    #
    def get_record_game_individual_result(self, context):
        map = IkaUtils.map2text(context['game']['map'])
        rule = IkaUtils.rule2text(context['game']['rule'])
        won = IkaUtils.getWinLoseText(
            context['game']['won'], win_text="勝ち", lose_text="負け", unknown_text="不明")

        t = IkaUtils.get_end_time(context)
        t_unix = int(time.mktime(t.timetuple()))
        t_str = t.strftime("%Y,%m,%d,%H,%M")
        s_won = IkaUtils.getWinLoseText(
            won, win_text="勝ち", lose_text="負け", unknown_text="不明")

        return "%s,%s,%s,%s,%s\n" % (t_unix, t_str, map, rule, won)

    ##
    # on_game_session_end Hook
    # @param self      The Object Pointer
    # @param context   IkaLog context
    #
    def on_game_session_end(self, context):
        IkaUtils.dprint('%s (enabled = %s)' % (self, self.enabled))

        if not self.enabled:
            return

        record = self.get_record_game_individual_result(context)
        self.write_record(record)

    ##
    # Constructor
    # @param self         The Object Pointer.
    # @param csv_filename CSV log file name
    #
    def __init__(self, csv_filename=None):
        self.enabled = (not csv_filename is None)
        self.csv_filename = csv_filename
