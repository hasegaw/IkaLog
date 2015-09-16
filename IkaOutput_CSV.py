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

# Needed in GUI mode
try:
	import wx
except:
	pass

## @package IkaOutput_CSV

## IkaOutput_CSV: IkaLog CSV Output Plugin
#
# Log Splatoon game results as CSV format.
class IkaOutput_CSV:

	def ApplyUI(self):
		self.enabled =           self.checkEnable.GetValue()
		self.csv_filename =      self.editCsvFilename.GetValue()

	def RefreshUI(self):
		self._internal_update = True
		self.checkEnable.SetValue(self.enabled)

		if not self.csv_filename is None:
			self.editCsvFilename.SetValue(self.csv_filename)
		else:
			self.editCsvFilename.SetValue('')

	def onConfigReset(self, context = None):
		self.enabled = False
		self.csv_filename = ''

	def onConfigLoadFromContext(self, context):
		self.onConfigReset(context)
		try:
			conf = context['config']['csv']
		except:
			conf = {}

		if 'Enable' in conf:
			self.enabled = conf['Enable']

		if 'CsvFilename' in conf:
			self.csv_filename = conf['CsvFilename']

		self.RefreshUI()
		return True

	def onConfigSaveToContext(self, context):
		context['config']['csv'] = {
			'Enable' : self.enabled,
			'CsvFilename': self.csv_filename,
		}

	def onConfigApply(self, context):
		self.ApplyUI()

	def onOptionTabCreate(self, notebook):
		self.panel = wx.Panel(notebook, wx.ID_ANY, size = (640, 360))
		self.page = notebook.InsertPage(0, self.panel, 'CSV')
		self.layout = wx.BoxSizer(wx.VERTICAL)
		self.panel.SetSizer(self.layout)
		self.checkEnable = wx.CheckBox(self.panel, wx.ID_ANY, u'CSVファイルへ戦績を出力する')
		self.editCsvFilename     = wx.TextCtrl(self.panel, wx.ID_ANY, u'hoge')

		try:
			layout = wx.GridSizer(2, 1)
		except:
			layout = wx.GridSizer(2)

		layout.Add(wx.StaticText(self.panel, wx.ID_ANY, u'CSV保存先ファイル'))
		layout.Add(self.editCsvFilename, flag = wx.EXPAND)

		self.layout.Add(self.checkEnable)
		self.layout.Add(layout)

	##
	# Write a line to text file.
	# @param self     The Object Pointer.
	# @param record   Record (text)
	#
	def writeRecord(self, record):
		try:
			csv_file = open(self.csv_filename, "a")
			csv_file.write(record)
			csv_file.close
		except:
			print("CSV: Failed to write CSV File")

	##
	# Generate a message for onGameIndividualResult.
	# @param self      The Object Pointer.
	# @param context   IkaLog context
	#
	def getRecordGameIndividualResult(self, context):
		map = IkaUtils.map2text(context['game']['map'])
		rule = IkaUtils.rule2text(context['game']['rule'])
		won = IkaUtils.getWinLoseText(context['game']['won'], win_text ="勝ち", lose_text = "負け", unknown_text = "不明")

		t = datetime.now()
		t_str = t.strftime("%Y,%m,%d,%H,%M")
		t_unix = int(time.mktime(t.timetuple()))
		s_won = IkaUtils.getWinLoseText(won, win_text ="勝ち", lose_text = "負け", unknown_text = "不明")

		return "%s,%s,%s,%s,%s\n" % (t_unix,t_str, map, rule, won)

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
	# @param self         The Object Pointer.
	# @param csv_filename CSV log file name
	#
	def __init__(self, csv_filename = None):
		if csv_filename is None:
			self.enabled = True
		self.csv_filename = csv_filename
