#!/usr/bin/env python3
# -*- coding: utf-8 -*-
from IkaUtils import *
import time

import cv2

## IkaOutput_Screen: IkaLog Output Plugin for Screen (video)
#
class IkaOutput_Screen:

	last_update = 0

	def onFrameRead(self, context):
		cv2.imshow('IkaLog', cv2.resize(context['engine']['frame'], self.video_size))

	def onFrameNext(self, context):
		if (self.wait_ms == 0):
			now = time.time()
			if (now - self.last_update) > 2:
				cv2.waitKey(1)
				self.last_update = now
		else:
			cv2.waitKey(self.wait_ms)

	##
	# Constructor
	# @param self         The Object Pointer.
	#
	def __init__(self, wait_ms = 1, size = (1280, 720)):
		self.wait_ms = wait_ms
		self.video_size = size
		pass
