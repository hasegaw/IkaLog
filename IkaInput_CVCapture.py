#!/usr/bin/env python3
# -*- coding: utf-8 -*-
import numpy as np
import cv2
import sys
import os

class IkaInput_CVCapture:
	out_width = 1280
	out_height = 720 
	need_resize = False

	def read(self):
		ret, frame = self.cap.read()

		if not ret:
			return None

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
