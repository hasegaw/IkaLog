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

import traceback
import threading

from .IkaUtils import *


# Needed in GUI mode
try:
    import wx
except:
    pass

# IkaLog Output Plugin: Show message on Console
#


class IkaOutput_OBS:

    def ApplyUI(self):
        self.enabled = self.checkEnable.GetValue()
        self.AutoRenameEnabled = self.checkAutoRenameEnable.GetValue()
        self.ControlOBS = self.editControlOBS.GetValue()
        self.dir = self.editDir.GetValue()

    def RefreshUI(self):
        self._internal_update = True
        self.checkEnable.SetValue(self.enabled)
        self.checkAutoRenameEnable.SetValue(self.AutoRenameEnabled)

        if not self.ControlOBS is None:
            self.editControlOBS.SetValue(self.ControlOBS)
        else:
            self.editControlOBS.SetValue('')

        if not self.dir is None:
            self.editDir.SetValue(self.dir)
        else:
            self.editDir.SetValue('')

    def onConfigReset(self, context=None):
        self.enabled = False
        self.AutoRenameEnabled = False
        self.ControlOBS = os.path.join(os.getcwd(), 'tools', 'ControlOBS.au3')
        self.dir = ''

    def onConfigLoadFromContext(self, context):
        self.onConfigReset(context)
        try:
            conf = context['config']['obs']
        except:
            conf = {}

        if 'Enable' in conf:
            self.enabled = conf['Enable']

        if 'AutoRenameEnable' in conf:
            self.AutoRenameEnabled = conf['AutoRenameEnable']

        if 'ControlOBS' in conf:
            self.ControlOBS = conf['ControlOBS']

        if 'Dir' in conf:
            self.dir = conf['Dir']

        self.RefreshUI()
        return True

    def onConfigSaveToContext(self, context):
        context['config']['obs'] = {
            'Enable': self.enabled,
            'AutoRenameEnable': self.AutoRenameEnabled,
            'ControlOBS': self.ControlOBS,
            'Dir': self.dir,
        }

    def onConfigApply(self, context):
        self.ApplyUI()

    def onOptionTabCreate(self, notebook):
        self.panel = wx.Panel(notebook, wx.ID_ANY)
        self.page = notebook.InsertPage(0, self.panel, 'OBS')
        self.layout = wx.BoxSizer(wx.VERTICAL)
        self.panel.SetSizer(self.layout)
        self.checkEnable = wx.CheckBox(
            self.panel, wx.ID_ANY, u'Open Broadcaster Software の録画／録画停止ボタンを自動操作する')
        self.checkAutoRenameEnable = wx.CheckBox(
            self.panel, wx.ID_ANY, u'録画ファイルの自動リネームを行う')
        self.editControlOBS = wx.TextCtrl(self.panel, wx.ID_ANY, u'hoge')
        self.editDir = wx.TextCtrl(self.panel, wx.ID_ANY, u'hoge')

        self.layout.Add(wx.StaticText(
            self.panel, wx.ID_ANY, u'ControlOBS.au3 パス'))
        self.layout.Add(self.editControlOBS, flag=wx.EXPAND)
        self.layout.Add(wx.StaticText(self.panel, wx.ID_ANY, u'録画フォルダ'))
        self.layout.Add(self.editDir, flag=wx.EXPAND)

        self.layout.Add(self.checkEnable)
        self.layout.Add(self.checkAutoRenameEnable)

        self.panel.SetSizer(self.layout)

    # Generate new MP4 filename.
    #
    # @param self    The object.
    # @param context IkaLog context.
    # @return        File name generated (without directory/path)
    def createMP4Filename(self, context):
        map = IkaUtils.map2text(context['game']['map'], unknown='マップ不明')
        rule = IkaUtils.rule2text(context['game']['rule'], unknown='ルール不明')
        won = IkaUtils.getWinLoseText(
            context['game']['won'], win_text='win', lose_text='lose')

        time_str = time.strftime("%Y%m%d_%H%M", time.localtime())
        newname = '%s_%s_%s_%s.mp4' % (time_str, map, rule, won)

        return newname

    # RunControlOBS
    def runControlOBS(self, mode):
        cmd = '%s %s' % (self.ControlOBS, mode)
        print('Running %s' % cmd)
        try:
            os.system(cmd)
        except:
            print(traceback.format_exc())

    # OnLobbyMatched
    #
    # @param self    The object.
    # @param context IkaLog context.
    def onLobbyMatched(self, context):
        if not self.enabled:
            return False

        self.runControlOBS('start')

    def worker(self):
        self.runControlOBS('stop')

    def onGameIndividualResult(self, context):
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

        if self.AutoRenameEnabled:
            os.environ['IKALOG_MP4_DESTNAME'] = '%s%s' % (
                self.dir, self.createMP4Filename(context))
            os.environ['IKALOG_MP4_DESTDIR'] = self.dir

        # Since we want to stop recording asyncnously,
        # This function is called by independent thread.
        # Note the context can be unexpected value.

        thread = threading.Thread(target=self.worker)
        thread.start()

    def __init__(self, ControlOBS=None, dir=None):
        self.enabled = (not ControlOBS is None)
        self.AutoRenameEnabled = (not dir is None)
        self.ControlOBS = ControlOBS
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

    obs = IkaOutput_OBS('P:/IkaLog/tools/ControlOBS.au3', dir='K:/')

    obs.onLobbyMatched(context)
    time.sleep(10)
    obs.onGameIndividualResult(context)
