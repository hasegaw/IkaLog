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
import numpy as np
import cv2
import sys
import os

class IkaInput_CVCapture:
	out_width = 1280
	out_height = 720 
	need_resize = False
	need_deinterlace = False
	offset = (0, 0)

	def read(self):
		ret, frame = self.cap.read()

		if not ret:
			return None

		if self.need_deinterlace:
			for y in range(frame.shape[0])[1::2]:
				frame[y,:] = frame[y - 1, :]

		if not (self.offset[0] == 0 and self.offset[1] == 0):
			ox = self.offset[0]
			oy = self.offset[1]

			sx1 = max(-ox, 0)
			sy1 = max(-oy, 0)

			dx1 = max(ox, 0)
			dy1 = max(oy, 0)

			w = min(self.out_width - dx1, self.out_width - sx1)
			h = min(self.out_height - dy1, self.out_height - sy1)

			frame[dy1:dy1 + h, dx1:dx1 + w] = frame[sy1:sy1 + h, sx1:sx1 + w]

		if self.need_resize:
			return cv2.resize(frame, (self.out_width, self.out_height))
		else:
			return frame

	def setResolution(self, width, height):
		self.cap.set(3, width)
		self.cap.set(4, height)
		self.need_resize = (width != self.out_width) or (height != self.out_height)

	def initCapture(self, source, width = 1280, height = 720):
		self.cap = cv2.VideoCapture(source)
		self.setResolution(width, height)

	def isWindows(self):
		try:
			os.uname()
		except AttributeError:
			return True

		return False

	def startCamera(self, source):
		if self.isWindows():
			self.initCapture(700 + source)
		else:
			self.initCapture(0 + source)

	def startRecordedFile(self, file):
		self.initCapture(file)

	#def __init__(self, source, width = 1280, height = 720):
	#	self.initCapture(source, width = width, height = height)

if __name__ == "__main__":
	obj = IkaInput_CVCapture()
	obj.startCamera(0)

	k = 0
	while k != 27:
		frame = obj.read()
		cv2.imshow('IkaInput_Capture', frame)
		k = cv2.waitKey(1) 
