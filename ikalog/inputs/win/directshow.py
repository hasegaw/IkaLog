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
from ikalog.inputs import VideoInput


class DirectShow(VideoInput):

    # override
    def _enumerate_sources_func(self):
        return self._videoinput_wrapper.get_device_list()

    def read_raw(self):
        if self._device_id is None:
            return None

        frame = self._videoinput_wrapper.get_pixels(
            self._device_id,
            parameters=(
                self._videoinput_wrapper.VI_BGR +
                self._videoinput_wrapper.VI_VERTICAL_FLIP
            )
        )

        return frame

    # override
    def _read_frame_func(self):
        frame = self.read_raw()
        return frame

    # override
    def _initialize_driver_func(self):
        pass

    # override
    def _cleanup_driver_func(self):
        pass

    # override
    def _is_active_func(self):
        return (self._device_id is not None)

    # override
    def _select_device_by_index_func(self, source, width=1280, height=720, framerate=59.94):
        device_id = int(source)
        vi = self._videoinput_wrapper
        self.lock.acquire()
        try:
            if self._device_id is not None:
                raise Exception('Need to deinit the device')

            formats = [
                {'width': width, 'height': height, 'framerate': None},
                {'width': width, 'height': height, 'framerate': framerate},
            ]

            for fmt in formats:
                if fmt['framerate']:
                    vi.set_framerate(device_id, fmt['framerate'])

                retval = vi.init_device(
                    device_id,
                    flags=self._videoinput_wrapper.DS_RESOLUTION,
                    width=fmt['width'],
                    height=fmt['height'],
                )
                if retval:
                    self._source_width = vi.get_frame_width(device_id)
                    self._source_height = vi.get_frame_height(device_id)

                    success = \
                        (width == self._source_width) and (
                            height == self._source_height)

                    if success or (not self.cap_optimal_input_resolution):
                        self._device_id = device_id
                        break

                    vi.deinit_device(device_id)
            # end of for loop

            if self._device_id is None:
                IkaUtils.dprint(
                    '%s: Failed to init the capture device %d' %
                    (self, device_id)
                )
        finally:
            self.lock.release()

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

    def __init__(self):
        self.strict_check = False
        self._device_id = None
        self._warned_resolution = False
        self._videoinput_wrapper = VideoInputWrapper()
        super(DirectShow, self).__init__()

if __name__ == "__main__":
    obj = DirectShow()

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
        k = cv2.waitKey(1)

        if k == ord('s'):
            import time
            cv2.imwrite('screenshot_%d.png' % int(time.time()), frame)
