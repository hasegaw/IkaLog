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

import time
import threading

import cv2

from ikalog.utils import *
from ikalog.inputs.win.videoinput_wrapper import VideoInputWrapper

class DirectShow(object):
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
        return self._videoinput_wrapper.get_device_list()

    def read_raw(self):
        if self._device_id is None:
            IkaUtils.dprint('%s: The deviec is not initialized.' % self)
            return None

        self.lock.acquire()
        try:
            frame = self._videoinput_wrapper.get_pixels(
                self._device_id,
                parameters=(self._videoinput_wrapper.VI_BGR +
                            self._videoinput_wrapper.VI_VERTICAL_FLIP)
            )
        finally:
            self.lock.release()

        return frame

    def read(self):
        frame = self.read_raw()

        if frame is None:
            # next frame is not ready.
            return None, None

        t = int(time.time() * 1000) - self._systime_launch
        return frame, t

        res720p = (frame.shape[0] == 720) and (frame.shape[1] == 1280)
        res1080p = (frame.shape[0] == 1080) and (frame.shape[1] == 1920)

        if not (res720p or res1080p):
            if not self._warned_resolution:
                params = (frame.shape[1], frame.shape[0])
                IkaUtils.dprint(
                    '解像度が不正です(%d, %d)。使用可能解像度: 1280x720 もしくは 1920x1080' % params)
                self._warned_resolution = True
            return None, None

        if t < self.last_t:
            IkaUtils.dprint(
                'FIXME: time position data rewinded. t=%s last_t=%s' % (t, self.last_t))
        self.last_t = t

        if self.need_resize:
            return cv2.resize(frame, (self.out_width, self.out_height)), t
        else:
            return frame, t

    def set_resolution(self, width, height):
        pass  # To Be implemented

    def init_capture(self, device_id, width=1280, height=720, framerate=59.94):
        self.lock.acquire()
        try:
            if self._device_id is not None:
                raise Exception('Need to deinit the device')

            self._videoinput_wrapper.set_framerate(device_id, framerate)
            retval = self._videoinput_wrapper.init_device(
                device_id,
                flags=self._videoinput_wrapper.DS_RESOLUTION,
                width=width,
                height=height,
            )

            if retval:
                self._device_id = device_id
                self._source_width = self._videoinput_wrapper.get_frame_width(
                    device_id)
                self._source_height = self._videoinput_wrapper.get_frame_height(
                    device_id)
                # FIXME: self.set_resolution(width, height)
        finally:
            self.lock.release()

        self.last_t = 0

    def start_camera(self, source_name):
        try:
            source = int(source_name)
        except:
            IkaUtils.dprint('%s: Looking up device name %s' %
                            (self, source_name))
            try:
                source_name = source_name.encode('utf-8')
            except:
                pass

            try:
                source = self.enumerate_input_sources().index(source_name)
            except:
                IkaUtils.dprint("%s: Input '%s' not found" %
                                (self, source_name))
                return False

        IkaUtils.dprint('%s: initalizing capture device %s' % (self, source))
        self.realtime = True
        self.init_capture(source)

    def __init__(self):
        self._device_id = None
        self.last_t = 0
        self._warned_resolution = False

        self._videoinput_wrapper = VideoInputWrapper()

if __name__ == "__main__":
    obj = DirectShow()

    list = obj.enumerate_input_sources()
    for n in range(len(list)):
        print("%d: %s" % (n, list[n]))

    dev = input("Please input number (or name) of capture device: ")

    obj.start_camera(dev)

    k = 0
    while k != 27:
        frame, t = obj.read()
        # print(frame, t)
        if frame is not None:
            cv2.imshow(obj.__class__.__name__, frame)
        k = cv2.waitKey(1)
