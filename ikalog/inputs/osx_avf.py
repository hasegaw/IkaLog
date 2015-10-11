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
        self.dll.readFrame.argtypes = [ ndpointer(ctypes.c_uint8, flags="C_CONTIGUOUS")]
        self.dll.readFrame.restype = None
        self.dll.selectCaptureDevice.argtypes = [ctypes.c_int]
        self.dll.selectCaptureDevice.restype = None

    def __init__(self):
        self.dll = None
        self._init_library()
        self.dll.setupAVCapture()

class AVFoundationCapture(object):
    cap = None
    out_width = 1280
    out_height = 720
    need_resize = False
    need_deinterlace = False
    realtime = True
    offset = (0, 0)

    _systime_launch = int(time.time() * 1000)

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
                frame[y, :] = frame[y - 1, :]

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
        t = int(time.time() * 1000) - self._systime_launch

        if self.need_resize:
            return cv2.resize(frame, (self.out_width, self.out_height)), t
        else:
            return frame, t

    def init_capture(self):
        self.lock.acquire()
        if not self.cap is None:
            self.cap = None
            sleep(0.1)

        self.cap = AVFoundationCaptureDevice()
        self.lock.release()

    def select_device(self, source_name):
        source = source_name # FIXME
        IkaUtils.dprint('%s: initializing capture device %s' % (self, source))

        # initialize target capture device
        frame, t = self.read()
        cv2.imshow(self.__class__.__name__, frame)
        cv2.waitKey(3000)

        self.cap.select_device(source_name)

    def start_camera_impl(self):
        self.init_capture()
        self.realtime = True
        self.from_file = False

        # initialize target capture device
        frame, t = self.read()
        cv2.imshow(self.__class__.__name__, frame)
        cv2.waitKey(3000)

    def start_camera(self, source_name):
        self.start_camera_impl()
        self.select_device(source_name)

    def restart_input(self):
        self.start_camera()

if __name__ == "__main__":
    obj = AVFoundationCapture()

    obj.start_camera_impl()
    dev = input("Please input number of capture device: ")
    obj.select_device(dev)

    k = 0
    while k != 27:
        frame, t = obj.read()
        image = cv2.resize(frame, (1280, 720))
        cv2.imshow(obj.__class__.__name__, image)
        k = cv2.waitKey(1)
