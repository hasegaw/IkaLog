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
import os
import threading
import time

import cv2
import numpy as np

from ikalog.utils import *


class DuplexedOutput(object):
    from_file = True
    fps = 120

    def read(self):
        if self.next_frame is None:
            return None, None

        next_frame = self.next_frame
        next_time = self.next_time

#        self.next_frame = None
#        self.next_time = None

        return next_frame, next_time

    def set_frame(self, frame, time):
        assert frame is not None
        p = self._points
        self.next_frame = cv2.resize(
            frame[p[1]:p[3], p[0]: p[2], :],
            (1280, 720),
            interpolation=cv2.INTER_NEAREST
        )

        self.next_time = time

    def set_bbox(self, points, enable):
        self._enable = enable
        self._points = points
        print('%s: set_bbox(%s, %s)' % (self, points, enable))

    def __init__(self, parent):
        self.next_frame = None
        self.next_time = None


class ConsolidatedInput(object):
    cap = None
    current_frame = None
    current_time = None
    out_width = 1280

    def next_frame(self):
        while (time.time() < self.blank_until):
            sleep(0.1)

        current_frame, current_time = self.source.read()

        if current_frame is None:
            return False

        cv2.imshow('Consolidated Input', cv2.resize(current_frame, (640, 360)))

        for view in self.outputs:
            view.set_frame(current_frame, current_time)

    def config_720p_single(self, port):
        for i in range(4):
            if (i + 1) == port:
                points = (0, 0, 1280, 720)
            else:
                points = (0, 0, 10, 10)
            self.outputs[i].set_bbox(points, enable=True)
        self._blank_until = time.time() + 0.5

    def config_720p_quad(self):
        w = 1280
        h = 720

        for i in range(4):
            x = i % 2
            y = int(i / 2)
            x1 = (w * x) / 2
            y1 = (h * y) / 2
            x2 = int(x1 + w / 2)
            y2 = int(y1 + h / 2)
            self.outputs[i].set_bbox((x1, y1, x2, y2), enable=True)
        self._blank_until = time.time() + 0.5

    def __init__(self, source):
        self.source = source
        self.blank_until = 0
        self.outputs = []
        for i in range(4):
            output = DuplexedOutput(self)
            self.outputs.append(output)
        self.config_720p_quad()
