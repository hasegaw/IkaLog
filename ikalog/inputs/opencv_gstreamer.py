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
from ikalog.inputs import CVFile


class GStreamer(CVFile):

    # override
    def _select_device_by_index_func(self, source):
        raise Exception('%s does not support selecting device by index.')

    # override
    def _select_device_by_name_func(self, source):
        self.lock.acquire()
        try:
            if self.is_active():
                self.video_capture.release()

            self.reset()
            self.video_capture = cv2.VideoCapture(source)

        finally:
            self.lock.release()

        return self.is_active()

    def __init__(self):
        self.video_capture = None
        super(GStreamer, self).__init__()


if __name__ == "__main__":
    import sys

    obj = GStreamer()
    obj.select_source(
        name='videotestsrc pattern = smpte ! videoconvert ! appsink'
    )

    k = 0
    while k != 27:
        frame = obj.read_frame()
        if frame is not None:
            cv2.imshow(obj.__class__.__name__, frame)
        cv2.waitKey(1)
