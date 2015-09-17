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
import ctypes
import time
import threading

from IkaUtils import *

# Needed in GUI mode
try:
	import wx
except:
	pass

class InputSourceEnumerator:
	def EnumWindows(self):
		numDevices = ctypes.c_int(0)
		r = self.dll.VI_Init()
		if (r != 0):
			return None

		r = self.dll.VI_GetDeviceNames(ctypes.pointer(numDevices))
		list = []
		for n in range(numDevices.value):
			friendly_name = self.dll.VI_GetDeviceName(n)
			list.append(friendly_name)

		self.dll.VI_Deinit()

		return list

	def EnumDummy(self):
		cameras = []
		for i in range(10):
			cameras.append('Input source %d' % (i + 1))

		return cameras

	def Enumerate(self):
		if IkaUtils.isWindows():
			try:
				return self.EnumWindows()
			except:
				IkaUtils.dprint('%s: Failed to enumerate DirectShow devices' % self)

		return self.EnumDummy()

	def __init__(self):
		if IkaUtils.isWindows():
			try:
				self.c_int_p = ctypes.POINTER(ctypes.c_int)

				ctypes.cdll.LoadLibrary('videoinput.dll')
				self.dll = ctypes.CDLL('videoinput.dll')

				self.dll.VI_Init.argtypes = []
				self.dll.VI_Init.restype = ctypes.c_int
				self.dll.VI_GetDeviceName.argtypes = [ctypes.c_int]
				self.dll.VI_GetDeviceName.restype = ctypes.c_char_p
				self.dll.VI_GetDeviceNames.argtypes = [self.c_int_p]
				self.dll.VI_GetDeviceNames.restype = ctypes.c_char_p
				self.dll.VI_GetDeviceName.argtypes = []
			except:
				IkaUtils.dprint("%s: Failed to initalize videoinput.dll" % self)


class IkaInput_CVCapture:
	cap = None
	out_width = 1280
	out_height = 720
	need_resize = False
	need_deinterlace = False
	realtime = True
	offset = (0, 0)

	_systime_launch = int(time.time() * 1000)

	## アマレコTV のキャプチャデバイス名
	DEV_AMAREC = "AmaRec Video Capture"

	source = 'amarec'
	SourceDevice = None
	Deinterlace = False
	File = ''

	lock = threading.Lock()

	def enumerateInputSources(self):
		return InputSourceEnumerator().Enumerate()

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

	def startCamera(self, source_name):

		try:
			source = int(source_name)
		except:
			IkaUtils.dprint('%s: Looking up device name %s' % (self, source_name))
			try:
				source_name = source_name.encode('utf-8')
			except:
				pass

			try:
				source = self.enumerateInputSources().index(source_name)
			except:
				IkaUtils.dprint("%s: Input '%s' not found" % (self, source_name))
				return False

		IkaUtils.dprint('%s: initalizing capture device %s' % (self, source))
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
		IkaUtils.dprint('RestartInput: source %s file %s device %s' % (self.source, self.File, self.SourceDevice))

		if self.source == 'camera':
			self.startCamera(self.SourceDevice)

		elif self.source == 'file':
			self.startRecordedFile(self.File)
		else:
			# Use amarec if available
			self.source = 'amarec'

		if self.source == 'amarec':
			self.startCamera(self.DEV_AMAREC)

		success = True
		if self.cap is None:
			success = False

		if success:
			if not self.cap.isOpened():
				success = False

		return success

	def ApplyUI(self):
		self.source = ''
		for control in [self.radioAmarecTV, self.radioCamera, self.radioFile]:
			if control.GetValue():
				self.source = {
					self.radioAmarecTV: 'amarec',
					self.radioCamera: 'camera',
					self.radioFile: 'file',
				}[control]

		self.SourceDevice = self.listCameras.GetItems()[self.listCameras.GetSelection()]
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
		if self.source == 'amarec':
			self.radioAmarecTV.SetValue(True)

		if self.source == 'camera':
			self.radioCamera.SetValue(True)

		if self.source == 'file':
			self.radioFile.SetValue(True)

		try:
			dev = self.SourceDevice
			index = self.listCameras.GetItems().index(dev)
			self.listCameras.SetSelection(index)
		except:
			IkaUtils.dprint('Current configured device is not in list')

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
		except:
			conf = {}

		self.source = ''
		try:
			if conf['Source'] in ['camera', 'file', u'camera', u'file']:
				self.source = conf['Source']
		except:
			pass

		if 'SourceDevice' in conf:
			try:
				self.SourceDevice = conf['SourceDevice']
			except:
				# FIXME
				self.SourceDevice = 0

		if 'File' in conf:
			self.File = conf['File']

		if 'Deinterlace' in conf:
			self.Deinterlace = conf['Deinterlace']

		self.RefreshUI()
		return self.restartInput()

	def onConfigSaveToContext(self, context):
		context['config']['cvcapture'] = {
			'Source': self.source,
			'File': self.File,
			'SourceDevice': self.SourceDevice,
			'Deinterlace': self.Deinterlace,
		}

	def onConfigApply(self, context):
		self.ApplyUI()

	def OnReloadDevicesButtonClick(self, event = None):
		cameras = self.enumerateInputSources()
		self.listCameras.SetItems(cameras)
		try:
			index = self.enumerateInputSources().index(self.SourceDevice)
			self.listCameras.SetSelection(index)
		except:
			IkaUtils.dprint('Error: Device not found')

	def onOptionTabCreate(self, notebook):
		self.panel = wx.Panel(notebook, wx.ID_ANY)
		self.page = notebook.InsertPage(0, self.panel, 'Input')

		cameras = self.enumerateInputSources()

		self.layout = wx.BoxSizer(wx.VERTICAL)
		self.panel.SetSizer(self.layout)
		self.radioAmarecTV = wx.RadioButton(self.panel, wx.ID_ANY, u'Capture through AmarecTV')
		self.radioAmarecTV.SetValue(True)

		self.radioCamera = wx.RadioButton(self.panel, wx.ID_ANY, u'Realtime Capture from HDMI grabber')
		self.radioFile = wx.RadioButton(self.panel, wx.ID_ANY, u'Read from pre-recorded video file (for testing)')
		self.editFile = wx.TextCtrl(self.panel, wx.ID_ANY, u'hoge')
		self.listCameras = wx.ListBox(self.panel, wx.ID_ANY, choices = cameras)
		self.listCameras.SetSelection(0)
		self.buttonReloadDevices = wx.Button(self.panel, wx.ID_ANY, u'Reload Devices')
		self.checkDeinterlace = wx.CheckBox(self.panel, wx.ID_ANY, u'Enable Deinterlacing (experimental)')

		self.layout.Add(wx.StaticText(self.panel, wx.ID_ANY, u'Select Input source:'))
		self.layout.Add(self.radioAmarecTV)
		self.layout.Add(self.radioCamera)
		self.layout.Add(self.listCameras, flag= wx.EXPAND)
		self.layout.Add(self.buttonReloadDevices)
		self.layout.Add(self.radioFile)
		self.layout.Add(self.editFile, flag = wx.EXPAND)
		self.layout.Add(self.checkDeinterlace)
		self.layout.Add(wx.StaticText(self.panel, wx.ID_ANY, u'Video Offset'))

		self.buttonReloadDevices.Bind(wx.EVT_BUTTON, self.OnReloadDevicesButtonClick)

if __name__ == "__main__":
	obj = IkaInput_CVCapture()

	list = InputSourceEnumerator().Enumerate()
	for n in range(len(list)):
		print("%d: %s" % (n, list[n]))

	dev = input("Please input number (or name) of capture device: ")

	obj.startCamera(dev)

	k = 0
	while k != 27:
		frame = obj.read()
		cv2.imshow('IkaInput_Capture', frame)
		k = cv2.waitKey(1)
