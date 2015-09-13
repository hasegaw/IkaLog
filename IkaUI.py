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
import threading
import yaml

from IkaInput_CVCapture import *
from IkaEngine import *
from IkaOutput_Console import *
from IkaOutput_Slack import *

from IkaPanel_Preview import *
from IkaPanel_Timeline import *
from IkaPanel_LastResult import *

class IkaLogGUI:

	## 現在の設定値をYAMLファイルにエクスポート
	#
	def saveCurrentConfig(self, context, filename = 'IkaConfig.yaml'):
		if not 'config' in context:
			context['config'] = {}
		for tab in self.tabs:
			tab.saveConfigToContext(context)

		yaml_file = open(filename, 'w')
		yaml_file.write(yaml.dump(context['config']))
		yaml_file.close

	## パネル切り替え時の処理
	#
	def OnSwitchPanel(self, event):
		activeButton = event.GetEventObject()

		for button in [self.buttonPreview, self.buttonLastResult, self.buttonTimeline]:
			panel = {
				self.buttonPreview: self.preview,
				self.buttonLastResult: self.lastResult,
				self.buttonTimeline: self.timeline,
			}[button]

			if button == activeButton:
				button.Disable()
				panel.Show()
				print('%s is shown' % panel)
			else:
				button.Enable()
				panel.Hide()
				print('%s is hidden' % panel)

		# リサイズイベントが発生しないと画面レイアウトが正しくならないので
		w, h = self.frame.GetClientSizeTuple()
		self.frame.SetSizeWH(w, h)

	## ('-' )
	#
	def OnA(self, event):
		context = {
			'config': {}
		}
		self.saveCurrentConfig(context)

	def CreateOptionsUI(self):
		self.notebookOptions = wx.Notebook(self.frame, wx.ID_ANY)

	def CreateButtonsUI(self):
		panel = self.frame
		self.buttonEnable     = wx.Button(panel, wx.ID_ANY, u'Enable')
		self.buttonPreview    = wx.Button(panel, wx.ID_ANY, u'Preview')
		self.buttonTimeline   = wx.Button(panel, wx.ID_ANY, u'Timeline')
		self.buttonLastResult = wx.Button(panel, wx.ID_ANY, u'Last Result')
		self.buttonOptions    = wx.Button(panel, wx.ID_ANY, u'Options')
		self.buttonDebugLog   = wx.Button(panel, wx.ID_ANY, u'Debug Log')

		self.buttonsLayout = wx.BoxSizer(wx.HORIZONTAL)
		self.buttonsLayout.Add(self.buttonEnable)
		self.buttonsLayout.Add(self.buttonPreview)
		self.buttonsLayout.Add(self.buttonTimeline)
		self.buttonsLayout.Add(self.buttonLastResult)
		self.buttonsLayout.Add(self.buttonOptions)
		self.buttonsLayout.Add(self.buttonDebugLog)

		self.buttonPreview.Bind(wx.EVT_BUTTON, self.OnSwitchPanel)
		self.buttonLastResult.Bind(wx.EVT_BUTTON, self.OnSwitchPanel)
		self.buttonTimeline.Bind(wx.EVT_BUTTON, self.OnSwitchPanel)

	def __init__(self):
		self.frame = wx.Frame(None, wx.ID_ANY, "IkaLog GUI", size=(700,500))

		self.layout = wx.BoxSizer(wx.VERTICAL)
		self.preview = PreviewPanel(self.frame, size=(640, 360))
		self.lastResult = LastResultPanel(self.frame, size=(640,360))
		self.timeline = TimelinePanel(self.frame, size=(640,200))
#		self.layout.Add(self.lastResult, flag = wx.EXPAND)
		self.layout.Add(self.preview, flag = wx.EXPAND)
		self.layout.Add(self.timeline, flag = wx.EXPAND)
		
		self.CreateButtonsUI()
		self.layout.Add(self.buttonsLayout)
		
		self.CreateOptionsUI()
		self.layout.Add(self.notebookOptions)

		self.tabs = [
#			IkaOptionTab_Fluentd(self),
#			IkaOptionTab_Hue(self),
#			IkaOptionTab_Twitter(self),
#			IkaOptionTab_Logging(self),
#			IkaOptionTab_Core(self),
		]

		self.frame.SetSizer(self.layout)

		self.buttonEnable.Bind(wx.EVT_BUTTON, self.OnA)

		self.frame.Show()


def uiThread():
	engine = IkaEngine()
	inputPlugin = IkaInput_CVCapture()
	#inputPlugin.startRecordedFile('/Users/hasegaw/Downloads/tag_match_lobby.mp4')
	inputPlugin.startRecordedFile('/Users/hasegaw/work/splatoon/hoko2_win.mp4')
	#inputPlugin.startRecordedFile('/Users/hasegaw/work/splatoon/hoko_game_mpeg4_6kbps.mp4')
	#inputPlugin.startRecordedFile('/Users/hasegaw/work/splatoon/scaled.avi')          # ファイルからの読み込み

	engine.setCapture(inputPlugin)
	outputPlugins = []
	outputPlugins.append(IkaOutput_Console())
	outputPlugins.append(gui.preview)
	outputPlugins.append(gui.lastResult)
	outputPlugins.append(gui.timeline)
	slack = IkaOutput_Slack()
	slack.onOptionTabCreate(gui.notebookOptions)
	slack.RefreshUI()

	engine.setPlugins(outputPlugins)

	engine.run()

if __name__ == "__main__":
	application  = wx.App()
	gui = IkaLogGUI()
	gui.frame.Show()

	thread = threading.Thread(target=uiThread)
	thread.start()
	application.MainLoop()
