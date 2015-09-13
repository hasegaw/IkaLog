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

from IkaUtils import *

# Needed on GUI mode
try:
	import wx
except:
	pass

## IkaOutput_Slack: IkaLog Output Plugin for Slack
#
# Post game results to Slack, using Incoming Hook
class IkaOutput_Slack:
	def onResetConfig(self, context = None):
		self.enabled = False
		self.url =''
		self.username = 'IkaLog'

	def onSaveConfigToContext(self, context):
		context['config']['slack'] = {
			'Enable': self.enabled,
			'url': self.url,
			'botName': self.username,
		}

	def ApplyUI(self):
		self.enabled  = self.checkEnable.GetValue()
		self.url      = self.editURL.GetValue()
		self.username = self.editBotName.GetValue()

	def RefreshUI(self):
		self._internal_update = True

		self.checkEnable.SetValue(self.enabled)
		self.editURL.SetValue(self.url)
		self.editBotName.SetValue(self.username)

		self._internal_update = False

	def OnApplyButtonClick(self, event):
		self.ApplyUI()

	def OnResetButtonClick(self, event):
		self.RefreshUI()

	def OnDefaultButtonClick(self, event):
		self.onResetConfig()
		self.RefreshUI()


	def onLoadConfigFromContext(self, context):
		self.OnResetConfig(context)
		if not ('slack' in context[config]):
			conf = context['config']['slack']
		else:
			conf = {}

		if 'Enable' in conf:
			self.enabled = conf['Enable']

		if 'url' in conf:
			self.url = conf['url']

		if 'botName' in conf:
			self.botName = conf['botName']

		self.RefreshUI()
		return True

	def onOptionTabCreate(self, notebook):
		self.panel = wx.Panel(notebook, wx.ID_ANY, size = (640, 360))
		self.page = notebook.InsertPage(0, self.panel, 'Slack')
		self.layout = wx.BoxSizer(wx.VERTICAL)

		self.checkEnable = wx.CheckBox(self.panel, wx.ID_ANY, u'Slack へ戦績を通知する')
		self.editURL = wx.TextCtrl(self.panel, wx.ID_ANY, u'http:')
		self.editBotName = wx.TextCtrl(self.panel, wx.ID_ANY, u'＜βコ3')

		self.applyButton = wx.Button(self.panel, wx.ID_ANY, u'反映')
		self.resetButton = wx.Button(self.panel, wx.ID_ANY, u'現行設定に戻す')
		self.defaultButton = wx.Button(self.panel, wx.ID_ANY, u'デフォルト設定に戻す')

		layout = wx.BoxSizer(wx.HORIZONTAL)
		layout.Add(wx.StaticText(self.panel, wx.ID_ANY, u'投稿者名'))
		layout.Add(self.editBotName, flag = wx.EXPAND)
		self.layout.Add(self.checkEnable)
		self.layout.Add(wx.StaticText(self.panel, wx.ID_ANY, u'Incoming WebHook API URL'))
		self.layout.Add(self.editURL, flag = wx.EXPAND)
		self.layout.Add(layout, flag = wx.EXPAND)

		layout = wx.BoxSizer(wx.HORIZONTAL)
		layout.Add(self.applyButton)
		layout.Add(self.resetButton)
		layout.Add(self.defaultButton)
		self.layout.Add(layout, flag = wx.EXPAND)

		self.panel.SetSizer(self.layout)

		self.applyButton.Bind(wx.EVT_BUTTON, self.OnApplyButtonClick)
		self.resetButton.Bind(wx.EVT_BUTTON, self.OnResetButtonClick)
		self.defaultButton.Bind(wx.EVT_BUTTON, self.OnDefaultButtonClick)

	##
	# Post a bot message to slack.
	# @param self     The Object Pointer.
	# @param text     Text message.
	# @param username Username.
	#
	def post(self, text = "", username = "＜8コ三"):
		try:
			import slackweb
			slack = slackweb.Slack(url = self.url)
			slack.notify(text = text, username = self.username)
		except:
			print("Slack: Failed to post a message to Slack")

	##
	# Generate a record for onGameIndividualResult.
	# @param self      The Object Pointer.
	# @param context   IkaLog context
	#
	def getTextGameIndividualResult(self, context):
		map = IkaUtils.map2text(context['game']['map'])
		rule = IkaUtils.rule2text(context['game']['rule'])
		won = IkaUtils.getWinLoseText(context['game']['won'], win_text ="勝ち", lose_text = "負け", unknown_text = "不明")
		return "%sで%sに%sました" % (map, rule, won)

	##
	# onGameIndividualResult Hook
	# @param self      The Object Pointer
	# @param context   IkaLog context
	#
	def onGameIndividualResult(self, context):
		s = self.getTextGameIndividualResult(context)

		fes_info = IkaUtils.playerTitle(IkaUtils.getMyEntryFromContext(context))
		if not fes_info is None:
			s = "%s (フェス %s)" % (s, fes_info)

		self.post(text = s, username = self.username)

	##
	# Check availability of modules this plugin depends on.
	# @param self      The Object Pointer.
	#
	def checkImport(self):
		try:
			import slackweb
		except:
			print("モジュール slackweb がロードできませんでした。 Slack 投稿ができません。")
			print("インストールするには以下のコマンドを利用してください。\n    pip install slackweb\n")

	##
	# Constructor
	# @param self     The Object Pointer.
	# @param url      Slack Incoming Hook Endpoint
	# @param username Name the bot use on Slack
	def __init__(self, url = None, username = "＜8ヨ"):
		self._internal_update = False
		self.url = url
		self.username = username
		self.enabled = (not url is None)
		self.checkImport()

if __name__ == "__main__":
	import sys
	obj = IkaOutput_Slack(
		url = sys.argv[1],
	)
	s = obj.getTextGameIndividualResult( {
			"game": {
				"map": {"name": "map_name"},
				"rule": {"name": "rule_name"},
				"won": True, }})
	print(s)
	obj.post(s)
