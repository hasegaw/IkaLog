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
from pynq.drivers.video import HDMI


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
        self.lock.acquire()
        try:
            if self.is_active():
                if self.hdmi_out is not None:
                    self.hdmi_out.stop()

                if self.hdmi_in is not None:
                    self.hdmi_in.stop()

            self.reset()
            self.hdmi_in = HDMI('in', init_timeout=10)
            self.hdmi_out = HDMI('out', frame_list=self.hdmi_in.frame_list)
            self.hdmi_out.mode(4) # 2=720p, 4=1080p
            time.sleep(1)

            #self.hdmi_out.stop()
            #self.hdmi_in.stop()
            #time.sleep(1)

            self.hdmi_out.start()
            self.hdmi_in.start()

            self.hdmi_in_geom = (self.hdmi_in.frame_width(), self.hdmi_in.frame_height())

            print('HDMI is capturing a video source of resolution %dx%d' %
                self.hdmi_in_geom)

            #if not self.hdmi_in.isOpened():
            #    IkaUtils.dprint(
            #        '%s: cv2.VideoCapture() failed to open the device' % self)
            #    self.hdmi_in = None

        except:
            print(traceback.format_exc())
            self.hdmi_in = None
            self.hdmi_out = None

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
        frame_raw = self.hdmi_in.frame_raw()
        frame = np.frombuffer(frame_raw, dtype=np.uint8)
        frame = frame.reshape(1080, 1920,3)
#        frame = frame[0:720, 0:1280, :]

        #if not ret:
        #    raise EOFError()

        return frame

    def __init__(self):
        self.hdmi_in = None
        self.hdmi_out = None
        super(PynqCapture, self).__init__()

if __name__ == "__main__":
    obj = PynqCapture()
    list = obj.enumerate_sources()
    for n in range(len(list)):
        IkaUtils.dprint("%d: %s" % (n, list[n]))

    dev = input("Please input number (or name) of capture device: ")
    obj.select_source(dev)

    k = 0
    while k != 27:
        frame = obj.read_frame()
        if 0 and (frame is not None):
            cv2.imshow(obj.__class__.__name__, frame)
            k = cv2.waitKey(1)
        if k == ord('s'):
            cv2.imwrite('test.png', frame)
