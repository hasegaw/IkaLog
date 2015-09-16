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

import wx
import time
import threading
import yaml

from IkaInput_CVCapture import *
from IkaEngine import *
from IkaOutput_Console import *
from IkaOutput_Slack import *
from IkaOutput_Twitter import *
from IkaOutput_OBS import *

from IkaPanel_Preview import *
from IkaPanel_Timeline import *
from IkaPanel_LastResult import *

from IkaUtils import *


class OptionsPanel(wx.Panel):
	## コールバックハンドラを設定
	#
	def Bind(self, event, func):
		self.handler[event] = func

	## イベントを発生させる
	#
	def RaiseEvent(self, event):
		if not (event in self.handler):
			return
		self.handler[event](self)

	def SetEventHandlerEnable(self, obj, enable):
		orig_state = obj.GetEvtHandlerEnabled()
		obj.SetEvtHandlerEnabled(enable)
		return orig_state

	## オプションボタン選択時の処理
	#
	def OnOptionButtonClick(self, event):
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
		self.layoutOptions.Add(self.notebookOptions, flag = wx.EXPAND)
		self.panelOptions.SetSizer(self.layoutOptions)

		buttonsLayout = wx.BoxSizer(wx.HORIZONTAL)
		self.buttonOptionApply = wx.Button(self.panelOptions, wx.ID_ANY, u'Apply')
		self.buttonOptionReset = wx.Button(self.panelOptions, wx.ID_ANY, u'Reset')
		self.buttonOptionLoadDefault = wx.Button(self.panelOptions, wx.ID_ANY, u'Load default')

		buttonsLayout.Add(self.buttonOptionApply)
		buttonsLayout.Add(self.buttonOptionReset)
		buttonsLayout.Add(self.buttonOptionLoadDefault)

		self.buttonOptionApply.Bind(wx.EVT_BUTTON, self.OnOptionButtonClick)
		self.buttonOptionReset.Bind(wx.EVT_BUTTON, self.OnOptionButtonClick)
		self.buttonOptionLoadDefault.Bind(wx.EVT_BUTTON, self.OnOptionButtonClick)

		self.layoutOptions.Add(buttonsLayout)
#		self.layout.Add(self.panelOptions, flag = wx.EXPAND)

		self.SetSizer(self.layoutOptions)
