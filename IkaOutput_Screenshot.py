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

## IkaOutput_Screenshot: IkaLog Output Plugin for Screenshots
#
# Save screenshots on certain events
class IkaOutput_Screenshot:
	def saveDrawing(self, context):
		x1 = 241
		x2 = x1 + 367
		y1 = 528
		y2 = y1 + 142

		drawing = context['engine']['frame'][y1:y2, x1:x2, :]

		basename = time.strftime("%Y%m%d_%H%M%S", time.localtime())
		destfile = "%s/miiverse_%s.png" % (self.dest_dir, basename)

		IkaUtils.writeScreenshot(destfile, drawing)
		print("スクリーンショット %s を保存しました" % destfile)

	##
	# onGameIndividualResult Hook
	# @param self      The Object Pointer
	# @param context   IkaLog context
	#
	def onGameIndividualResult(self, context):
		basename = time.strftime("%Y%m%d_%H%M", time.localtime())
		destfile = "%s/ikabattle_%s.png" % (self.dest_dir, basename)

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
	# @param dest_dir     Destionation directory (Relative path, or absolute path)
	#
	def __init__(self, dest_dir):
		self.dest_dir = dest_dir
