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
import time
import threading

import cv2
from ikalog.utils import *


class GStreamer(object):
    cap = None
    out_width = 1280
    out_height = 720
    from_file = False
    need_resize = False
    need_deinterlace = False
    realtime = False
    offset = (0, 0)

    _systime_launch = int(time.time() * 1000)

    lock = threading.Lock()

    def read_raw(self):
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
            raise EOFError

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
                'FIXME: time position data rewinded. t=%x last_t=%x' % (t, self.last_t))
        self.last_t = t

        if self.need_resize:
            return cv2.resize(frame, (self.out_width, self.out_height)), t
        else:
            return frame, t

    def init_capture(self, source):
        self.lock.acquire()
        try:
            if not self.cap is None:
                self.cap.release()

            self.cap = cv2.VideoCapture(source)
            self.last_t = 0
        finally:
            self.lock.release()

    def start_gstreamer(self, source):
        self.init_capture(source)

        # ToDo: タイミング情報がとれるかをテストする

    def __init__(self):
        self.last_t = 0

if __name__ == "__main__":
    import sys

    obj = GStreamer()
    obj.start_gstreamer("videotestsrc pattern = smpte ! videoconvert ! appsink")
    obj.need_resize = True

    k = 0
    while k != 27:
        for i in range(100):
            frame, t = obj.read()
        cv2.imshow(obj.__class__.__name__, frame)
        k = cv2.waitKey(1)
