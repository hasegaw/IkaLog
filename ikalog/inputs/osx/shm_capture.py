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
        self.dll.readFrame_shm(self.dest_buffer)
        # ToDo: Error check.

        frame = self.dest_buffer[:, :, 0:3]
        assert(frame.shape[2] == 3)

        return True, cv2.cvtColor(frame, cv2.COLOR_RGB2BGR)

    def select_device(self, device_num):
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
        self.dll.readFrame_shm.argtypes = [
            ndpointer(ctypes.c_uint8, flags="C_CONTIGUOUS")]
        self.dll.readFrame_shm.restype = None
        self.dll.selectCaptureDevice.argtypes = [ctypes.c_int]
        self.dll.selectCaptureDevice.restype = None

    def __init__(self):
        self.dll = None
        self._init_library()
        self.dll.setupAVCapture()


class SharedMemoryCapture(VideoInput):

    def _read_frame_func(self):
        cur_tick = self.get_current_timestamp()
        try:
            last_tick = self.last_tick
        except:
            last_tick = 0

        if last_tick is None:
            next_tick = cur_tick
        elif self.fps_requested is not None:
            next_tick = last_tick + (1000 / self.fps_requested)
        else:
            next_tick = cur_tick

        while (cur_tick < next_tick):
            time.sleep(0.01)
            cur_tick = self.get_current_timestamp()

        self.last_tick = next_tick

        #####

        ret, frame = self.cap.read()

        return frame

    def _initialize_driver_func(self):
        IkaUtils.dprint('%s: initializing class' % self)
        self.lock.acquire()
        if not self.cap is None:
            self.cap = None
            sleep(0.1)

        self.cap = AVFoundationCaptureDevice()
        self.lock.release()

    def _is_active_func(self):
        return True

    def _select_device_by_index_func(self, source):
        print('%s: Doesn''t support _select_device_by_index_func()' % self)

    def _select_device_by_name_func(self, source):
        print('%s: Doesn''t support _select_device_by_name_func()' % self)

    def __init__(self):
        self.cap = None
        super(SharedMemoryCapture, self).__init__()

if __name__ == "__main__":
    obj = SharedMemoryCapture()
    obj.set_frame_rate(10)

    k = 0
    while k != 27:
        frame = obj.read_frame()
        print(obj.get_current_timestamp())
        cv2.imshow(obj.__class__.__name__, frame)
        k = cv2.waitKey(1)

        if k == ord('s'):
            import time
            cv2.imwrite('screenshot_%d.png' % int(time.time()), frame)
