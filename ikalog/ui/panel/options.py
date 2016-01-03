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

from .last_result import *


class OptionsPanel(wx.Panel):
    # コールバックハンドラを設定
    #

    def Bind(self, event, func):
        self.handler[event] = func

    # イベントを発生させる
    #
    def RaiseEvent(self, event):
        if not (event in self.handler):
            return
        self.handler[event](self)

    def SetEventHandlerEnable(self, obj, enable):
        orig_state = obj.GetEvtHandlerEnabled()
        obj.SetEvtHandlerEnabled(enable)
        return orig_state

    # オプションボタン選択時の処理
    #
    def on_option_button_click(self, event):
        activeButton = event.GetEventObject()

        event_name = {
            self.buttonOptionApply: 'optionsApply',
            self.buttonOptionReset: 'optionsReset',
            self.buttonOptionLoadDefault: 'optionsLoadDefault',
        }[activeButton]
        self.RaiseEvent(event_name)

    def __init__(self, *args, **kwargs):
        self.handler = {}

        wx.Panel.__init__(self, *args, **kwargs)

        self.panelOptions = self
        self.notebookOptions = wx.Notebook(self.panelOptions, wx.ID_ANY)
        self.layoutOptions = wx.BoxSizer(wx.VERTICAL)

        buttonsLayout = wx.BoxSizer(wx.HORIZONTAL)
        self.buttonOptionApply = wx.Button(
            self.panelOptions, wx.ID_ANY, u'Apply')
        self.buttonOptionReset = wx.Button(
            self.panelOptions, wx.ID_ANY, u'Reset')
        self.buttonOptionLoadDefault = wx.Button(
            self.panelOptions, wx.ID_ANY, u'Load default')

        buttonsLayout.Add(self.buttonOptionApply)
        buttonsLayout.Add(self.buttonOptionReset)
        buttonsLayout.Add(self.buttonOptionLoadDefault)

        self.buttonOptionApply.Bind(wx.EVT_BUTTON, self.on_option_button_click)
        self.buttonOptionReset.Bind(wx.EVT_BUTTON, self.on_option_button_click)
        self.buttonOptionLoadDefault.Bind(
            wx.EVT_BUTTON, self.on_option_button_click)

        self.layoutOptions.Add(buttonsLayout, flag=wx.EXPAND | wx.TOP, border=10)
        self.layoutOptions.Add(self.notebookOptions, flag=wx.EXPAND)

        self.SetSizer(self.layoutOptions)
