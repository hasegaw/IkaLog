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
import time
import threading

from IkaUtils import *

# Needed in GUI mode
try:
	import wx
except:
	pass

class IkaInput_CVCapture:
	cap = None
	out_width = 1280
	out_height = 720
	need_resize = False
	need_deinterlace = False
	realtime = True
	offset = (0, 0)

	_systime_launch = int(time.time() * 1000)

	source = ''
	CameraIndex = 0
	Deinterlace = False
	File = ''

	lock = threading.Lock()

	def read(self):
		if self.cap is None:
			return None, None

		self.lock.acquire()
		ret, frame = self.cap.read()
		self.lock.release()

		if not ret:
			return None, None

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

		t = None
		if not self.realtime:
			try:
				t = self.cap.get(cv2.CAP_PROP_POS_MSEC)
			except:
				pass
			if t is None:
				print('Cannot get video position...')
				self.realtime = True

		if self.realtime:
			t = int(time.time() * 1000) - self._systime_launch

		if self.need_resize:
			return cv2.resize(frame, (self.out_width, self.out_height)), t
		else:
			return frame, t

	def setResolution(self, width, height):
		self.cap.set(3, width)
		self.cap.set(4, height)
		self.need_resize = (width != self.out_width) or (height != self.out_height)

	def initCapture(self, source, width = 1280, height = 720):
		self.lock.acquire()
		if not self.cap is None:
			self.cap.release()

		self.cap = cv2.VideoCapture(source)
		self.setResolution(width, height)
		self.lock.release()

	def isWindows(self):
		try:
			os.uname()
		except AttributeError:
			return True

		return False

	def startCamera(self, source):
		IkaUtils.dprint('%s: initalizing capture device %d' % (self, source))
		self.realtime = True
		if self.isWindows():
			self.initCapture(700 + source)
		else:
			self.initCapture(0 + source)

	def startRecordedFile(self, file):
		IkaUtils.dprint('%s: initalizing pre-recorded video file %s' % (self, file))
		self.realtime = False
		self.initCapture(file)

	def restartInput(self):
		print(self.source, self.File, self.CameraIndex)
		if self.source == 'camera':
			self.initCapture(self.CameraIndex)
		elif self.source == 'file':
			self.startRecordedFile(self.File)
		else:
			self.cap = None
			IkaUtils.dprint('No input is set up.')

		success = True
		if self.cap is None:
			success = False

		if not success:
			if not self.cap.isOpened():
				success = False

		return success

	def ApplyUI(self):
		self.source = ''
		for control in [self.radioCamera, self.radioFile]:
			if control.GetValue():
				self.source = {
					self.radioCamera: 'camera',
					self.radioFile: 'file',
				}[control]

		self.CameraIndex = self.listCameras.GetSelection()
		self.File        = self.editFile.GetValue()
		self.Deinterlace = self.checkDeinterlace.GetValue()

		# この関数は GUI 動作時にしか呼ばれない。カメラが開けなかった
		# 場合にメッセージを出す
		if not self.restartInput():
			r = wx.MessageDialog(None, u'キャプチャデバイスの初期化に失敗しました。設定を見直してください', 'Error',
				wx.OK | wx.ICON_ERROR).ShowModal()
			IkaUtils.dprint("%s: failed to activate input source >>>>" % (self))
		else:
			IkaUtils.dprint("%s: activated new input source" % self)

	def RefreshUI(self):
		if self.source == 'camera':
			self.radioCamera.SetValue(True)

		if self.source == 'file':
			self.radioFile.SetValue(True)

		self.listCameras.SetSelection(self.CameraIndex)

		if not self.File is None:
			self.editFile.SetValue('')
		else:
			self.editFile.SetValue(self.File)

		self.checkDeinterlace.SetValue(self.Deinterlace)

	def onConfigReset(self, context = None):
		# さすがにカメラはリセットしたくないな
		pass

	def onConfigLoadFromContext(self, context):
		self.onConfigReset(context)
		try:
			conf = context['config']['cvcapture']
			print(context['config']['cvcapture'])
		except:
			conf = {}

		self.source = ''
		try:
			if conf['Source'] in ['camera', 'file', u'camera', u'file']:
				self.source = conf['Source']
		except:
			pass

		if 'CameraIndex' in conf:
			try:
				self.CameraIndex = int(conf['CameraIndex'])
			except:
				# FIXME
				self.CameraIndex = 0

		if 'File' in conf:
			self.File = conf['File']

		if 'Deinterlace' in conf:
			self.Deinterlace = conf['Deinterlace']

		self.RefreshUI()

		if self.source != '':
			return self.restartInput()

		return False

	def onConfigSaveToContext(self, context):
		context['config']['cvcapture'] = {
			'Source': self.source,
			'File': self.File,
			'CameraIndex': self.CameraIndex,
			'Deinterlace': self.Deinterlace,
		}
		print(context['config']['cvcapture'])

	def onConfigApply(self, context):
		self.ApplyUI()

	def onOptionTabCreate(self, notebook):
		self.panel = wx.Panel(notebook, wx.ID_ANY, size = (640, 360))
		self.page = notebook.InsertPage(0, self.panel, 'Input')

		cameras = [ 'a', 'b' ]

		self.layout = wx.BoxSizer(wx.VERTICAL)
		self.panel.SetSizer(self.layout)
		self.radioCamera = wx.RadioButton(self.panel, wx.ID_ANY, u'Realtime Capture from HDMI grabber')
		self.radioFile = wx.RadioButton(self.panel, wx.ID_ANY, u'Read from pre-recorded video file (for testing)')
		self.editFile = wx.TextCtrl(self.panel, wx.ID_ANY, u'hoge')
		self.listCameras = wx.ListBox(self.panel, wx.ID_ANY, choices = cameras)
		self.buttonReloadDevices = wx.Button(self.panel, wx.ID_ANY, u'Reload Devices')
		self.checkDeinterlace = wx.CheckBox(self.panel, wx.ID_ANY, u'Enable Deinterlacing (experimental)')

		self.layout.Add(wx.StaticText(self.panel, wx.ID_ANY, u'Select Input source:'))
		self.layout.Add(self.radioCamera)
		self.layout.Add(self.listCameras, flag= wx.EXPAND)
		self.layout.Add(self.buttonReloadDevices)
		self.layout.Add(self.radioFile)
		self.layout.Add(self.editFile, flag = wx.EXPAND)
		self.layout.Add(self.checkDeinterlace)
		self.layout.Add(wx.StaticText(self.panel, wx.ID_ANY, u'Video Offset'))

if __name__ == "__main__":
	obj = IkaInput_CVCapture()
	obj.startCamera(0)

	k = 0
	while k != 27:
		frame = obj.read()
		cv2.imshow('IkaInput_Capture', frame)
		k = cv2.waitKey(1)
