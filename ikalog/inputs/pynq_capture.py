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
import traceback

import cv2
import numpy as np
from pynq.drivers import video
from pynq.drivers.video import HDMI
from cffi import FFI

from ikalog.utils import *
from ikalog.inputs import VideoInput


class PynqCapture(VideoInput):

    # override
    def _enumerate_sources_func(self):
        if IkaUtils.isWindows():
            return self._videoinput_wrapper.get_device_list()
        return ['Device Enumeration not supported']

    # override
    def _initialize_driver_func(self):
        # OpenCV File doesn't need pre-initialization.
        self._cleanup_driver_func()

    # override
    def _cleanup_driver_func(self):
        self.lock.acquire()
        try:
            if self.ffi is not None:
                self.ffi = None

            if self.framebuffer is not None:
                for fb in self.framebuffer:
                    del fb

            if self.hdmi_out is not None:
                self.hdmi_out.stop()
                self.hdmi_out = None

            if self.hdmi_in is not None:
                self.hdmi_in.stop()
                self.hdmi_in = None

            self.reset()
        finally:
            self.lock.release()

    # override
    def _is_active_func(self):
        return (self.hdmi_in is not None)

    # override
    def _select_device_by_index_func(self, source):
        self._cleanup_driver_func()
        self.lock.acquire()
        try:
            self.ffi = FFI()
            self.hdmi_in = HDMI('in', init_timeout=10)
            self.hdmi_in.start()

            # TODO: under development
            if False and self._enable_output:
                self.hdmi_out = HDMI('out', frame_list=self.hdmi_in.frame_list)
                mode = self._select_output_mode(self.hdmi_in.frame_width(), self.hdmi_in.frame_height())
                self.hdmi_out.mode(mode)

            time.sleep(1)

            if self.hdmi_out is not None:
                self.hdmi_out.start()

            self.hdmi_in_geom = \
                (self.hdmi_in.frame_width(), self.hdmi_in.frame_height())

            self.framebuffer = []
            for i in range(video.VDMA_DICT['NUM_FSTORES']):
                pointer = self.ffi.cast('uint8_t *', self.hdmi_in.frame_addr(i))
                #buffer_size = video.MAX_FRAME_WIDTH * video.MAX_FRAME_HEIGHT * 3 # 3 == sizeof(RGB)
                buffer_size = self.hdmi_in_geom[0] * self.hdmi_in_geom[1] * 3
                _bf = self.ffi.buffer(pointer, buffer_size)
                bf = np.frombuffer(_bf,np.uint8).reshape(self.hdmi_in_geom[1],self.hdmi_in_geom[0],3)
                #self.framebuffer.append(bf[:self.hdmi_in_geom[1],:self.hdmi_in_geom[0],:])
                self.framebuffer.append(bf)

            IkaUtils.dprint('%s: resolution %dx%d' % (self, self.hdmi_in_geom[0], self.hdmi_in_geom[1]))

        except:
            print(traceback.format_exc())
            self.hdmi_in = None
            self.hdmi_out = None
            if self.framebuffer is not None:
                for fb in self.framebuffer:
                    del fb
            self.ffi = None

        finally:
            self.lock.release()

        self.systime_base = time.time()
        return self.is_active()

    # override
    def _select_device_by_name_func(self, source):
        IkaUtils.dprint('%s: Select device by name "%s"' % (self, source))

        try:
            index = self.enumerate_sources().index(source)
        except ValueError:
            IkaUtils.dprint('%s: Input "%s" not found' % (self, source))
            return False

        IkaUtils.dprint('%s: "%s" -> %d' % (self, source, index))
        self._select_device_by_index_func(index)

    # override
    def _get_current_timestamp_func(self):
        return int((time.time() - self.systime_base) * 1000)

    # override
    def _read_frame_func(self):
        t1 = time.time()
        if self._mode == 1 and hasattr(self.hdmi_in, 'frame_raw2'):
            # Modified version of PYNQ library has faster capture function.
            frame = self.hdmi_in.frame_raw2()
        elif self._mode == 2:
            index = self.hdmi_in.frame_index()
            self.hdmi_in.frame_index_next()
            frame = self.framebuffer[index]
        else:
            # This function is supported in original version, but 10X slow.
            frame_raw = self.hdmi_in.frame_raw()
            frame = np.frombuffer(frame_raw, dtype=np.uint8)
            frame = frame.reshape(1080, 1920, 3)
            frame = frame[0:720, 0:1280, :]
        t2 = time.time()
        if self._debug:
            print('read_frame_func: %6.6f' % (t2 - t1))
        return frame

    def _select_output_mode(self, width, height):
        if width == 640 and height == 480:
            return 0
        if width == 800 and height == 600:
            return 1
        if width == 1280 and height == 720:
            return 2
        if width == 1280 and height == 1024:
            return 3
        if width == 1920 and height == 1080:
            return 4
        raise Exception("Specific output frame size not supported: %dx%d"%(width,height))

    def __init__(self, enable_output=False, debug=False, mode=2):
        self.hdmi_in = None
        self.hdmi_out = None
        self.ffi = None
        self.framebuffer = None
        self._enable_output = enable_output
        self._debug = debug
        self._mode = mode

        IkaUtils.dprint(
            '%s: debug %s enable_output %s mode %s' %
            (self, self._debug, self._enable_output, self._mode))

        super(PynqCapture, self).__init__()

if __name__ == "__main__":
    from PIL import Image
    obj = PynqCapture(debug=True,enable_output=False)
    obj.select_source(0)
    time.sleep(1)

    k = 0
    t = time.time()
    while (time.time() - t) < 100:
        frame = obj.read_frame()
        Image.frombytes("RGB",(frame.shape[1],frame.shape[0]),bytes(frame[:,:,::-1])).save("dump/test_%d.jpg"%k)
        k = k+1
