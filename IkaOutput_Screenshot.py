#!/usr/bin/env python3
# -*- coding: utf-8 -*-

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
