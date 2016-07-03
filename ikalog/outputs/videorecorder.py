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

import time
import os
import traceback
import threading

from ikalog.utils import *


# Needed in GUI mode
try:
    import wx
except:
    pass

# IkaLog Output Plugin: Show message on Console
#

_ = Localization.gettext_translation('video_recorder', fallback=True).gettext

class OBS(object):

    def apply_ui(self):
        self.enabled = self.checkEnable.GetValue()
        self.auto_rename_enabled = self.checkAutoRenameEnable.GetValue()
        self.control_obs = self.editControlOBS.GetValue()
        self.dir = self.editDir.GetValue()

    def refresh_ui(self):
        self._internal_update = True
        self.checkEnable.SetValue(self.enabled)
        self.checkAutoRenameEnable.SetValue(self.auto_rename_enabled)

        if not self.control_obs is None:
            self.editControlOBS.SetValue(self.control_obs)
        else:
            self.editControlOBS.SetValue('')

        if not self.dir is None:
            self.editDir.SetValue(self.dir)
        else:
            self.editDir.SetValue('')

    def on_config_reset(self, context=None):
        self.enabled = False
        self.auto_rename_enabled = False
        self.control_obs = os.path.join(os.getcwd(), 'tools', 'ControlOBS.au3')
        self.dir = ''

    def on_config_load_from_context(self, context):
        self.on_config_reset(context)
        try:
            conf = context['config']['obs']
        except:
            conf = {}

        if 'Enable' in conf:
            self.enabled = conf['Enable']

        if 'AutoRenameEnable' in conf:
            self.auto_rename_enabled = conf['AutoRenameEnable']

        if 'ControlOBS' in conf:
            self.control_obs = conf['ControlOBS']

        if 'Dir' in conf:
            self.dir = conf['Dir']

        self.refresh_ui()
        return True

    def on_config_save_to_context(self, context):
        context['config']['obs'] = {
            'Enable': self.enabled,
            'AutoRenameEnable': self.auto_rename_enabled,
            'ControlOBS': self.control_obs,
            'Dir': self.dir,
        }

    def on_config_apply(self, context):
        self.apply_ui()

    def on_option_tab_create(self, notebook):
        self.panel = wx.Panel(notebook, wx.ID_ANY)
        self.panel_name = _('Video Recorder')
        self.layout = wx.BoxSizer(wx.VERTICAL)
        self.panel.SetSizer(self.layout)
        self.checkEnable = wx.CheckBox(
            self.panel, wx.ID_ANY, _('Enable control of video recording applications'))
        self.checkAutoRenameEnable = wx.CheckBox(
            self.panel, wx.ID_ANY, _('Automatically rename recorded videos'))
        self.editControlOBS = wx.TextCtrl(self.panel, wx.ID_ANY, u'hoge')
        self.editDir = wx.TextCtrl(self.panel, wx.ID_ANY, u'hoge')

        self.layout.Add(wx.StaticText(
            self.panel, wx.ID_ANY, _('Path to controller scripts (ControlOBS.au3)')))
        self.layout.Add(self.editControlOBS, flag=wx.EXPAND)
        self.layout.Add(wx.StaticText(self.panel, wx.ID_ANY, _('Recordings Folder')))
        self.layout.Add(self.editDir, flag=wx.EXPAND)

        self.layout.Add(self.checkEnable)
        self.layout.Add(self.checkAutoRenameEnable)

        self.panel.SetSizer(self.layout)

    # Generate new MP4 filename.
    #
    # @param self    The object.
    # @param context IkaLog context.
    # @return        File name generated (without directory/path)
    def create_mp4_filename(self, context):
        map = IkaUtils.map2text(context['game']['map'], unknown='マップ不明')
        rule = IkaUtils.rule2text(context['game']['rule'], unknown='ルール不明')
        won = IkaUtils.getWinLoseText(
            context['game']['won'], win_text='win', lose_text='lose')

        time_str = time.strftime("%Y%m%d_%H%M", time.localtime())
        newname = '%s_%s_%s_%s.mp4' % (time_str, map, rule, won)

        return newname

    # RunControlOBS
    def run_control_obs(self, mode):
        cmd = '%s %s' % (self.control_obs, mode)
        print('Running %s' % cmd)
        try:
            os.system(cmd)
        except:
            print(traceback.format_exc())

    # OnLobbyMatched
    #
    # @param self    The object.
    # @param context IkaLog context.
    def on_lobby_matched(self, context):
        if not self.enabled:
            return False

        self.run_control_obs('start')

    def worker(self):
        self.run_control_obs('stop')

    def on_game_individual_result(self, context):
        if not self.enabled:
            return False

        # Set Environment variables.
        map = IkaUtils.map2text(context['game']['map'], unknown='unknown')
        rule = IkaUtils.rule2text(context['game']['rule'], unknown='unknown')
        won = IkaUtils.getWinLoseText(
            context['game']['won'], win_text='win', lose_text='lose', unknown_text='unknown')

        os.environ['IKALOG_STAGE'] = map
        os.environ['IKALOG_RULE'] = rule
        os.environ['IKALOG_WON'] = won
        #os.environ['IKALOG_TIMESTAMP'] = time.strftime("%Y%m%d_%H%M", context['game']['timestamp'])

        if self.auto_rename_enabled:
            os.environ['IKALOG_MP4_DESTNAME'] = os.path.join(
                self.dir,
                self.create_mp4_filename(context)
            )
            os.environ['IKALOG_MP4_DESTDIR'] = os.path.join(
                self.dir,
                '', # terminate with delimiter (slash or backslash.)
            )

        # Since we want to stop recording asyncnously,
        # This function is called by independent thread.
        # Note the context can be unexpected value.

        thread = threading.Thread(target=self.worker)
        thread.start()

    def __init__(self, control_obs=None, dir=None):
        self.enabled = (not control_obs is None)
        self.auto_rename_enabled = (not dir is None)
        self.control_obs = control_obs
        self.dir = dir

if __name__ == "__main__":
    from datetime import datetime
    import time
    context = {
        'game': {
            'map': {'name': 'mapname'},
            'rule': {'name': 'rulename'},
            'won': True,
            'timestamp': datetime.now(),
        }
    }

    obs = OBS('P:/IkaLog/tools/ControlOBS.au3', dir='K:/')

    obs.on_lobby_matched(context)
    time.sleep(10)
    obs.on_game_individual_result(context)
