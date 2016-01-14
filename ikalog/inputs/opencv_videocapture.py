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
import os
import ctypes
import time
import threading

import cv2

from ikalog.utils import *


# Needed in GUI mode
try:
    import wx
except:
    pass


class InputSourceEnumerator(object):

    def enum_windows(self):
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

    def enum_dummy(self):
        cameras = []
        for i in range(10):
            cameras.append('Input source %d' % (i + 1))

        return cameras

    def enumerate(self):
        if IkaUtils.isWindows():
            try:
                cameras = self.enum_windows()
                if len(cameras) > 1:
                    return cameras
            except:
                IkaUtils.dprint(
                    '%s: Failed to enumerate DirectShow devices' % self)

        return self.enum_dummy()

    def __init__(self):
        if IkaUtils.isWindows():
            videoinput_dll = os.path.join('lib', 'videoinput.dll')
            try:
                self.c_int_p = ctypes.POINTER(ctypes.c_int)

                ctypes.cdll.LoadLibrary(videoinput_dll)
                self.dll = ctypes.CDLL(videoinput_dll)

                self.dll.VI_Init.argtypes = []
                self.dll.VI_Init.restype = ctypes.c_int
                self.dll.VI_GetDeviceName.argtypes = [ctypes.c_int]
                self.dll.VI_GetDeviceName.restype = ctypes.c_char_p
                self.dll.VI_GetDeviceNames.argtypes = [self.c_int_p]
                self.dll.VI_GetDeviceNames.restype = ctypes.c_char_p
                self.dll.VI_GetDeviceName.argtypes = []
            except:
                IkaUtils.dprint(
                    "%s: Failed to initalize %s" % (self, videoinput_dll))


class CVCapture(object):
    cap = None
    out_width = 1280
    out_height = 720
    from_file = False
    need_resize = False
    need_deinterlace = False
    realtime = True
    offset = (0, 0)

    _systime_launch = int(time.time() * 1000)

    lock = threading.Lock()

    def enumerate_input_sources(self):
        return InputSourceEnumerator().enumerate()

    def read_raw(self):
        if self.cap is None:
            return None

        self.lock.acquire()
        try:
            ret, frame = self.cap.read()
        finally:
            self.lock.release()

        if not ret:
            return None

        # self.last_raw_size = frame.shape[0:1]
        return frame

    def read(self):
        frame = self.read_raw()

        if frame is None:
            return None, None

        res720p = (frame.shape[0] == 720) and (frame.shape[1] == 1280)
        res1080p = (frame.shape[0] == 1080) and (frame.shape[1] == 1920)

        if not (res720p or res1080p):
            if not self._warned_resolution:
                params = (frame.shape[1], frame.shape[0])
                IkaUtils.dprint(
                    '解像度が不正です(%d, %d)。使用可能解像度: 1280x720 もしくは 1920x1080' % params)
                self._warned_resolution = True
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
        if not self.realtime:
            try:
                t = self.cap.get(cv2.CAP_PROP_POS_MSEC)
            except:
                pass
            if t is None:
                IkaUtils.dprint('Cannot get video position...')
                self.realtime = True

        if self.realtime:
            t = int(time.time() * 1000) - self._systime_launch

        if t < self.last_t:
            IkaUtils.dprint(
                'FIXME: time position data rewinded. t=%s last_t=%s' % (t, self.last_t))
        self.last_t = t

        if self.need_resize:
            return cv2.resize(frame, (self.out_width, self.out_height)), t
        else:
            return frame, t

    def set_resolution(self, width, height):
        self.cap.set(3, width)
        self.cap.set(4, height)
        self.need_resize = (width != self.out_width) or (
            height != self.out_height)

    def init_capture(self, source, width=1280, height=720):
        self.lock.acquire()
        try:
            if not self.cap is None:
                self.cap.release()

            self.cap = cv2.VideoCapture(source)
            self.set_resolution(width, height)
            self.last_t = 0
        finally:
            self.lock.release()

    def start_camera(self, source_name):
        try:
            source = int(source_name)
        except ValueError:
            IkaUtils.dprint('%s: Looking up device name %s' %
                            (self, source_name))
            source = None

            if IkaUtils.isWindows():
                from ikalog.inputs.win.videoinput_wrapper import VideoInputWrapper
                devices_list = VideoInputWrapper().get_device_list()
                try:
                    source = devices_list.index(source_name)
                except ValueError:
                    pass

        if source is None:
            IkaUtils.dprint("%s: Input '%s' not found" % (self, source_name))
            return None

        IkaUtils.dprint('%s: initalizing capture device %s' % (self, source))
        self.realtime = True
        if IkaUtils.isWindows():
            self.init_capture(700 + source)
        else:
            self.init_capture(0 + source)

    def __init__(self):
        self.last_t = 0
        self._warned_resolution = False

if __name__ == "__main__":
    obj = CVCapture()

    list = InputSourceEnumerator().enumerate()
    for n in range(len(list)):
        print("%d: %s" % (n, list[n]))

    dev = input("Please input number (or name) of capture device: ")

    obj.start_camera(dev)

    k = 0
    while k != 27:
        frame, t = obj.read()
        cv2.imshow(obj.__class__.__name__, frame)
        k = cv2.waitKey(1)
