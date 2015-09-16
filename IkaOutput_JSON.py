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

from datetime import datetime
import time
import json

# Needed in GUI mode
try:
	import wx
except:
	pass

## IkaOutput_JSON: IkaLog Output Plugin for JSON Logging
#
# Write JSON Log file
class IkaOutput_JSON:


	def ApplyUI(self):
		self.enabled =           self.checkEnable.GetValue()
		self.json_filename =      self.editJsonFilename.GetValue()

	def RefreshUI(self):
		self._internal_update = True
		self.checkEnable.SetValue(self.enabled)

		if not self.json_filename is None:
			self.editJsonFilename.SetValue(self.json_filename)
		else:
			self.editJsonFilename.SetValue('')

	def onConfigReset(self, context = None):
		self.enabled = False
		self.json_filename = ''

	def onConfigLoadFromContext(self, context):
		self.onConfigReset(context)
		try:
			conf = context['config']['json']
		except:
			conf = {}

		if 'Enable' in conf:
			self.enabled = conf['Enable']

		if 'JsonFilename' in conf:
			self.json_filename = conf['JsonFilename']

		self.RefreshUI()
		return True

	def onConfigSaveToContext(self, context):
		context['config']['json'] = {
			'Enable' : self.enabled,
			'JsonFilename': self.json_filename,
		}

	def onConfigApply(self, context):
		self.ApplyUI()

	def onOptionTabCreate(self, notebook):
		self.panel = wx.Panel(notebook, wx.ID_ANY, size = (640, 360))
		self.page = notebook.InsertPage(0, self.panel, 'JSON')
		self.layout = wx.BoxSizer(wx.VERTICAL)
		self.panel.SetSizer(self.layout)
		self.checkEnable = wx.CheckBox(self.panel, wx.ID_ANY, u'JSONファイルへ戦績を出力する')
		self.editJsonFilename     = wx.TextCtrl(self.panel, wx.ID_ANY, u'hoge')

		try:
			layout = wx.GridSizer(2, 1)
		except:
			layout = wx.GridSizer(2)

		layout.Add(wx.StaticText(self.panel, wx.ID_ANY, u'JSON保存先ファイル'))
		layout.Add(self.editJsonFilename, flag = wx.EXPAND)

		self.layout.Add(self.checkEnable)
		self.layout.Add(layout)

	##
	# Write a line to text file.
	# @param self     The Object Pointer.
	# @param record   Record (text)
	#
	def writeRecord(self, record):
		try:
			json_file = open(self.json_filename, "a")
			json_file.write(record)
			json_file.close
		except:
			print("JSON: Failed to write JSON file")

	##
	# Generate a record for onGameIndividualResult.
	# @param self      The Object Pointer.
	# @param context   IkaLog context
	#
	def getRecordGameIndividualResult(self, context):
		map = IkaUtils.map2text(context['game']['map'])
		rule = IkaUtils.rule2text(context['game']['rule'])
		won = IkaUtils.getWinLoseText(context['game']['won'], win_text ="win", lose_text = "lose", unknown_text = "unknown")

		t = datetime.now()
		t_str = t.strftime("%Y,%m,%d,%H,%M")
		t_unix = int(time.mktime(t.timetuple()))

		record = { 'time': t_unix, 'event': 'GameResult', 'map': map, 'rule': rule, 'result': won }
		return json.dumps(record, separators=(',',':')) + "\n"

	##
	# onGameIndividualResult Hook
	# @param self      The Object Pointer
	# @param context   IkaLog context
	#
	def onGameIndividualResult(self, context):
		IkaUtils.dprint('%s (enabled = %s)' % (self, self.enabled))

		if not self.enabled:
			return

		record = self.getRecordGameIndividualResult(context)
		self.writeRecord(record)

	##
	# Constructor
	# @param self          The Object Pointer.
	# @param json_filename JSON log file name
	#
	def __init__(self, json_filename = None):
		self.enabled = (not json_filename is None)
		self.json_filename = json_filename
