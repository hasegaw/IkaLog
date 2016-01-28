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

import copy
import ctypes
import os
import threading
import time

import cv2
import numpy as np
from numpy.ctypeslib import ndpointer

from ikalog.utils import *
from ikalog.inputs import VideoInput


class AVFoundationCaptureDevice(object):

    def read(self):
        self.dll.readFrame(self.dest_buffer)
        # ToDo: Error check.

        frame = self.dest_buffer[:, :, 0:3]
        assert(frame.shape[2] == 3)

        return True, copy.deepcopy(frame)

    def select_device(self, device_num):
        try:
            n = int(device_num)
            self.dll.selectCaptureDevice(n)
        except:
            pass

    def __del__hoge__(self):
        if hasattr(self, 'dll'):
            self.dll.stopAVCapture()

    def _init_library(self):
        self.dest_buffer = np.zeros((720, 1280, 4), np.uint8)

        libavf_dll = os.path.join('lib', 'libavf_ctypes.so')
        ctypes.cdll.LoadLibrary(libavf_dll)

        self.dll = ctypes.CDLL(libavf_dll)
        self.dll.setupAVCapture.argtypes = None
        self.dll.setupAVCapture.restype = None
        self.dll.stopAVCapture.argtypes = None
        self.dll.stopAVCapture.restype = None
        self.dll.readFrame.argtypes = [
            ndpointer(ctypes.c_uint8, flags="C_CONTIGUOUS")]
        self.dll.readFrame.restype = None
        self.dll.selectCaptureDevice.argtypes = [ctypes.c_int]
        self.dll.selectCaptureDevice.restype = None

    def __init__(self):
        self.dll = None
        self._init_library()
        self.dll.setupAVCapture()


class AVFoundationCapture(VideoInput):

    def _read_frame_func(self):

        ret, frame = self.cap.read()
        if not ret:
            return None

        return frame

    def _cleanup_driver_func(self):
        self.lock.acquire()
        if not self.cap is None:
            self.cap = None
            sleep(0.1)
        self.lock.release()

    def _initialize_driver_func(self):
        IkaUtils.dprint('%s: initializing class' % self)
        self.lock.acquire()
        if not self.cap is None:
            self.cap = None
            sleep(0.1)

        self.cap = AVFoundationCaptureDevice()

        time.sleep(3)

        self.lock.release()

    def _is_active_func(self):
        return True

    def _select_device_by_index_func(self, source):
        IkaUtils.dprint('%s: initializing capture device %s' % (self, source))

        # initialize target capture device
        frame = self.read_frame()
        cv2.imshow(self.__class__.__name__, frame)
        cv2.waitKey(3000)

        self.cap.select_device(source)
        self.last_tick = self.get_tick()

    def _select_device_by_name_func(self, source):
        IkaUtils.dprint(
            '%s: Doesn''t support _select_device_by_name_func()' % self)

    def __init__(self):
        self.cap = None
        super(AVFoundationCapture, self).__init__()

if __name__ == "__main__":

    obj = AVFoundationCapture()
    dev = input("Please input number of capture device: ")
    cv2.imshow(obj.__class__.__name__, np.zeros((240, 320), dtype=np.uint8))
    obj.select_source(dev)

    k = 0
    while k != 27:
        frame = obj.read_frame()
        image = cv2.resize(frame, (1280, 720))
        cv2.imshow(AVFoundationCapture.__name__, image)
        k = cv2.waitKey(1)

        if k == ord('s'):
            import time
            cv2.imwrite('screenshot_%d.png' % int(time.time()), frame)
