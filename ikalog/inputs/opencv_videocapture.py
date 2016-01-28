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
from ikalog.inputs.win.videoinput_wrapper import VideoInputWrapper
from ikalog.inputs import VideoInput


class CVCapture(VideoInput):

    def _enumerate_sources_func(self):
        if IkaUtils.isWindows():
            return self._videoinput_wrapper.get_device_list()
        return ['Device Enumeration not supported']

    def _initialize_driver_func(self):
        # OpenCV File doesn't need pre-initialization.
        self._cleanup_driver_func()

    def _cleanup_driver_func(self):
        self.lock.acquire()
        try:
            if self.video_capture is not None:
                self.video_capture.release()
                self.video_capture = None
            self.reset()
        finally:
            self.lock.release()

    def _is_active_func(self):
        return \
            hasattr(self, 'video_capture') and \
            (self.video_capture is not None)

    def _select_device_by_index_func(self, source):
        self.lock.acquire()
        try:
            if self.is_active():
                self.video_capture.release()

            self.reset()
            self.video_capture = cv2.VideoCapture(int(source))

            if not self.video_capture.isOpened():
                IkaUtils.dprint(
                    '%s: cv2.VideoCapture() failed to open the device' % self)
                self.video_capture = None

            self.systime_base = time.time()
        except:
            self.dprint(traceback.format_exc())
            self.video_capture = None

        finally:
            self.lock.release()

        return self.is_active()

    def _select_device_by_name_func(self, source):
        IkaUtils.dprint('%s: Select device by name "%s"' % (self, source))

        try:
            index = self.enumerate_sources().index(source)
        except ValueError:
            IkaUtils.dprint('%s: Input "%s" not found' % (self, source))
            return False

        IkaUtils.dprint('%s: "%s" -> %d' % (self, source, index))
        self._select_device_by_index_func(index)

    def _get_current_timestamp_func(self):
        return int((time.time() - self.systime_base) * 1000)

    def _read_frame_func(self):
        ret, frame = self.video_capture.read()
        if not ret:
            raise EOFError()

        return frame

    def __init__(self):
        self.video_capture = None
        if IkaUtils.isWindows():
            self._videoinput_wrapper = VideoInputWrapper()
        super(CVCapture, self).__init__()

if __name__ == "__main__":
    obj = CVCapture()
    list = obj.enumerate_sources()
    for n in range(len(list)):
        IkaUtils.dprint("%d: %s" % (n, list[n]))

    dev = input("Please input number (or name) of capture device: ")
    obj.select_source(dev)

    k = 0
    while k != 27:
        frame = obj.read_frame()
        if frame is not None:
            cv2.imshow(obj.__class__.__name__, frame)
        cv2.waitKey(1)
