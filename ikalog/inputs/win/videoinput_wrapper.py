#!/usr/bin/env python3
# -*- coding: utf-8 -*-
#
#  IkaLog
#  ======
#  Copyright (C) 2015 Takeshi HASEGAWA
#
#  Licensed under the Apache License, Version 2.0 (the 'License');
#  you may not use this file except in compliance with the License.
#  You may obtain a copy of the License at
#
#      http://www.apache.org/licenses/LICENSE-2.0
#
#  Unless required by applicable law or agreed to in writing, software
#  distributed under the License is distributed on an 'AS IS' BASIS,
#  WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
#  See the License for the specific language governing permissions and
#  limitations under the License.
#

import ctypes
from ctypes import c_char_p, c_double, c_int
import numpy as np
import os
import time
import threading

import cv2

from ikalog.utils import *

c_int_p = ctypes.POINTER(c_int)


class VideoInputWrapper(object):
    VI_COMPOSITE = 0
    VI_S_VIDEO = 1
    VI_TUNER = 2
    VI_USB = 3
    VI_1394 = 4

    VI_NTSC_M = 0
    VI_PAL_B = 1
    VI_PAL_D = 2
    VI_PAL_G = 3
    VI_PAL_H = 4
    VI_PAL_I = 5
    VI_PAL_M = 6
    VI_PAL_N = 7
    VI_PAL_NC = 8
    VI_SECAM_B = 9
    VI_SECAM_D = 10
    VI_SECAM_G = 11
    VI_SECAM_H = 12
    VI_SECAM_K = 13
    VI_SECAM_K1 = 14
    VI_SECAM_L = 15
    VI_NTSC_M_J = 16
    VI_NTSC_433 = 17

    VI_MEDIASUBTYPE_RGB24 = 0
    VI_MEDIASUBTYPE_RGB32 = 1
    VI_MEDIASUBTYPE_RGB555 = 2
    VI_MEDIASUBTYPE_RGB565 = 3
    VI_MEDIASUBTYPE_YUY2 = 4
    VI_MEDIASUBTYPE_YVYU = 5
    VI_MEDIASUBTYPE_YUYV = 6
    VI_MEDIASUBTYPE_IYUV = 7
    VI_MEDIASUBTYPE_UYVY = 8
    VI_MEDIASUBTYPE_YV12 = 9
    VI_MEDIASUBTYPE_YVU9 = 0
    VI_MEDIASUBTYPE_Y411 = 11
    VI_MEDIASUBTYPE_Y41P = 12
    VI_MEDIASUBTYPE_Y211 = 13
    VI_MEDIASUBTYPE_AYUV = 14
    VI_MEDIASUBTYPE_Y800 = 15
    VI_MEDIASUBTYPE_Y8 = 16
    VI_MEDIASUBTYPE_GREY = 17
    VI_MEDIASUBTYPE_MJPG = 18

    VI_BGR = 0x01
    VI_VERTICAL_FLIP = 0x02

    DS_RESOLUTION = 0x01
    DS_CONNECTION = 0x20

    def __del__(self):
        self.dll.VI_Deinit()

    def get_device_names(self):
        num_devices = c_int(0)
        r = self.dll.VI_GetDeviceNames(ctypes.pointer(num_devices))
        # ToDo: error validation
        return num_devices.value

    def get_device_name(self, index):
        friendly_name_b = self.dll.VI_GetDeviceName(index)
        friendly_name = friendly_name_b.decode('ascii', errors='replace')
        return friendly_name

    def get_device_list(self):
        num_devices = self.get_device_names()
        device_list = []

        for n in range(num_devices):
            device_list.append(self.get_device_name(n))

        return device_list

    def get_frame_height(self, index):
        return self.dll.VI_GetFrameHeight(index)

    def get_frame_width(self, index):
        return self.dll.VI_GetFrameWidth(index)

    def init_device(self, index, settings=None, flags=None, width=None, height=None, connection=None):
        settings = np.array([flags, width, height], dtype=np.intc)
        return self.dll.VI_InitDevice(index, settings) == 0

    def deinit_device(self, index):
        self.dll.VI_DeinitDevice(index)

    def set_blocking(self, enable):
        self.dll.VI_SetBlocking(enable)

    def set_framerate(self, index, framerate):
        self.dll.VI_SetFramerate(index, framerate)

    def has_new_frame(self, index):
        return self.dll.VI_HasNewFrame(index)

    def get_buffer_size(self, index):
        return self.dll.VI_GetBufferSize(index)

    def get_buffer_geometry(self, index):
        (buf_size, w, h) = (
            self.get_buffer_size(index),
            self.get_frame_width(index),
            self.get_frame_height(index),
        )

        assert buf_size > 0
        bpp = buf_size // (w * h)
        assert bpp == int(bpp)
        return (h, w, bpp)

    def get_pixels(self, index, parameters=0):
        geom = self.get_buffer_geometry(index)

        frame_buffer = np.zeros(geom, np.uint8)
        assert frame_buffer.flags['C_CONTIGUOUS']

        retval = self.dll.VI_GetPixels(index, frame_buffer, parameters)
        if retval:
            return frame_buffer

        return None

    def _load_library(self):
        videoinput_dll = os.path.join('lib', 'videoinput.dll')

        ctypes.cdll.LoadLibrary(videoinput_dll)
        self.dll = ctypes.CDLL(videoinput_dll)

        self.dll.VI_Init.argtypes = []
        self.dll.VI_Init.restype = c_int

        self.dll.VI_GetDeviceName.argtypes = [c_int]
        self.dll.VI_GetDeviceName.restype = c_char_p

        self.dll.VI_GetDeviceNames.argtypes = [c_int_p]
        self.dll.VI_GetDeviceNames.restype = c_char_p

        self.dll.VI_InitDevice.argtypes = [
            c_int,
            np.ctypeslib.ndpointer(dtype=np.intc, flags='C_CONTIGUOUS'),
        ]
        self.dll.VI_InitDevice.restype = c_int

        self.dll.VI_DeinitDevice.argtypes = [c_int]
        self.dll.VI_DeinitDevice.restype = None

        self.dll.VI_SetBlocking.argtypes = [c_int]
        self.dll.VI_SetBlocking.restype = None

        self.dll.VI_SetFramerate.argtypes = [c_int, c_double]
        self.dll.VI_SetFramerate.restype = None

        self.dll.VI_GetFrameHeight.argtypes = [c_int]
        self.dll.VI_GetFrameHeight.restype = c_int

        self.dll.VI_GetFrameWidth.argtypes = [c_int]
        self.dll.VI_GetFrameWidth.restype = c_int

        self.dll.VI_HasNewFrame.argtypes = [c_int]
        self.dll.VI_HasNewFrame.restype = c_int

        self.dll.VI_GetBufferSize.argtypes = [c_int]
        self.dll.VI_GetBufferSize.restype = c_int

        self.dll.VI_GetPixels.argtypes = [
            c_int,
            np.ctypeslib.ndpointer(dtype=np.uint8, flags='C_CONTIGUOUS'),
            c_int
        ]
        self.dll.VI_GetPixels.restype = c_int

    def __new__(cls, *args, **kwargs):
        if not hasattr(cls, '__instance__'):
            cls.__instance__ = \
                super(VideoInputWrapper, cls).__new__(cls, *args, **kwargs)
            cls.__instance__._load_library()
            cls.__instance__.dll.VI_Init()
        return cls.__instance__
