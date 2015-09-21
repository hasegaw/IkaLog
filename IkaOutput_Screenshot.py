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
from IkaScene_PlazaUserStat import * #Fixme...

import cv2
import time
import os

# Needed in GUI mode
try:
	import wx
except:
	pass

## IkaOutput_Screenshot: IkaLog Output Plugin for Screenshots
#
# Save screenshots on certain events
class IkaOutput_Screenshot:

	def ApplyUI(self):
		self.resultDetailEnabled = self.checkResultDetailEnable.GetValue()
		self.miiverseDrawingEnabled = self.checkMiiverseDrawingEnable.GetValue()
		self.dir =               self.editDir.GetValue()

	def RefreshUI(self):
		self._internal_update = True
		self.checkResultDetailEnable.SetValue(self.resultDetailEnabled)
		self.checkMiiverseDrawingEnable.SetValue(self.miiverseDrawingEnabled)

		if not self.dir is None:
			self.editDir.SetValue(self.dir)
		else:
			self.editDir.SetValue('')

	def onConfigReset(self, context = None):
		self.resultDetailEnabled = False
		self.miiverseDrawingEnabled = False
		self.dir = os.path.join(os.getcwd(), 'screenshots')

	def onConfigLoadFromContext(self, context):
		self.onConfigReset(context)
		try:
			conf = context['config']['screenshot']
		except:
			conf = {}

		if 'ResultDetailEnable' in conf:
			self.resultDetailEnabled = conf['ResultDetailEnable']

		if 'MiiverseDrawingEnable' in conf:
			self.miiverseDrawingEnabled = conf['MiiverseDrawingEnable']

		if 'Dir' in conf:
			self.dir = conf['Dir']

		self.RefreshUI()
		return True

	def onConfigSaveToContext(self, context):
		context['config']['screenshot'] = {
			'ResultDetailEnable' : self.resultDetailEnabled,
			'MiiveseDrawingEnable' : self.miiverseDrawingEnabled,
			'Dir': self.dir,
		}

	def onConfigApply(self, context):
		self.ApplyUI()

	def onOptionTabCreate(self, notebook):
		self.panel = wx.Panel(notebook, wx.ID_ANY)
		self.page = notebook.InsertPage(0, self.panel, 'Screenshot')
		self.layout = wx.BoxSizer(wx.VERTICAL)
		self.panel.SetSizer(self.layout)
		self.checkResultDetailEnable = wx.CheckBox(self.panel, wx.ID_ANY, u'戦績画面のスクリーンショットを保存する')
		self.checkMiiverseDrawingEnable = wx.CheckBox(self.panel, wx.ID_ANY, u'広場で他プレイヤーの画面を開いた際、投稿を自動保存する')
		self.editDir = wx.TextCtrl(self.panel, wx.ID_ANY, u'hoge')

		self.layout.Add(wx.StaticText(self.panel, wx.ID_ANY, u'スクリーンショット保存先ディレクトリ'))
		self.layout.Add(self.editDir, flag = wx.EXPAND)
		self.layout.Add(self.checkResultDetailEnable)
		self.layout.Add(self.checkMiiverseDrawingEnable)

		self.panel.SetSizer(self.layout)

	def saveDrawing(self, context):
		x1 = 241
		x2 = x1 + 367
		y1 = 528
		y2 = y1 + 142

		drawing = context['engine']['frame'][y1:y2, x1:x2, :]

		timestr = time.strftime("%Y%m%d_%H%M%S", time.localtime())
		destfile = os.path.join(self.dir, 'miiverse_%s.png' % timestr)

		IkaUtils.writeScreenshot(destfile, drawing)
		print("スクリーンショット %s を保存しました" % destfile)

	##
	# onGameIndividualResult Hook
	# @param self      The Object Pointer
	# @param context   IkaLog context
	#
	def onGameIndividualResult(self, context):
		timestr = time.strftime("%Y%m%d_%H%M%S", time.localtime())
		destfile = os.path.join(self.dir, 'ikabattle_%s.png' % timestr)

		IkaUtils.writeScreenshot(destfile, context['engine']['frame'])
		print("スクリーンショット %s を保存しました" % destfile)

	def onKeyPress(self, context, key):
		if not (key == 0x53 or key == 0x73):
			return False

		if IkaScene_PlazaUserStat().match(context):
			self.saveDrawing(context)

	##
	# Constructor
	# @param self         The Object Pointer.
	# @param dir          Destionation directory (Relative path, or absolute path)
	#
	def __init__(self, dest_dir = None):
		self.resultDetailEnabled = (not dest_dir is None)
		self.miiverseDrawingEnabled = False
		self.dir = dest_dir
