#!/usr/bin/env python3
# -*- coding: utf-8 -*-
from IkaUtils import *

import cv2
import time

## IkaOutput_Screenshot: IkaLog Output Plugin for Screenshots
#
# Save screenshots on certain events
class IkaOutput_Screenshot:

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

	##
	# Constructor
	# @param self         The Object Pointer.
	# @param dest_dir     Destionation directory (Relative path, or absolute path)
	#
	def __init__(self, dest_dir):
		self.dest_dir = dest_dir
