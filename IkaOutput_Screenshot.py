#!/usr/bin/env python3
# -*- coding: utf-8 -*-
import cv2
import time

class IkaOutput_Screenshot:
	def onGameStart(self, frame, map_name, mode_name):
		pass

	def onResultDetail(self, frame, map_name, mode_name, won):
		basename = time.strftime("%Y%m%d_%H%M", time.localtime())
		destfile = "%s/ikabattle_%s.png" % (self.dest_dir, basename)
		try:
			cv2.imwrite(destfile, frame)
		except:
			print("Screenshot: failed")
		finally:
			pass

	def __init__(self, dest_dir):
		self.dest_dir = dest_dir
