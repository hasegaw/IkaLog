#!/usr/bin/env python3
# -*- coding: utf-8 -*-
#
#  IkaLog
#  ======
#  Copyright (C) 2017 Takeshi HASEGAWA
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

import re
import sys

import cv2
import numpy as np

from ikalog.scenes.scene import Scene
from ikalog.utils import *


"""
Y position

y0
    ^^^^^^^
y1
      5:00
y2
    vvvvvvv
y3
"""
y0 = 16
y1 = 14 + 20
y2 = 14 + 43
y3 = 16 + 62


class TimerReader(object):
    _p_threshold = 0.9
    time_regexp = re.compile('(\d+)\.(\d+)')

    def read_time(self, img):
        img = cv2.cvtColor(img, cv2.COLOR_GRAY2BGR)
        timestr = self._number_recoginizer.match(img)

        result = re.match(self.time_regexp, timestr)
        if not result:
            return False
        m = int(result.group(1))
        s = int(result.group(2))

        valid = (m <= 5) and (s <= 59)

        if valid:
            self._time_counter = m * 60 + s

        return valid

    def match(self, img):
        img_timestr = img[y1: y2, 610:610 + 60]

        img_timer_black = matcher.MM_DARK()(img_timestr)
        img_timer_white = matcher.MM_WHITE(visibility=(100, 255))(img_timestr)
        img_timer_yellow = matcher.MM_COLOR_BY_HUE(
            hue=(35 - 5, 35 + 5), visibility=(100, 255))(img_timestr)

        img_test = img_timer_black | img_timer_white | img_timer_yellow
        orig_hist = cv2.calcHist([img_test], [0], None, [2], [0, 256])
        self._p = (orig_hist[1] / (orig_hist[0] + orig_hist[1]))

        time_valid = False
        if self._p > self._p_threshold:
            time_valid = self.read_time(255 - img_timer_black)

            if time_valid:
                print('残り時間',  self._time_counter)

        return self._p > self._p_threshold

    def __init__(self):
        self._number_recoginizer = NumberRecoginizer()


class V2GameTimerIcon(Scene):

    def reset(self):
        super(V2GameTimerIcon, self).reset()

        self._last_event_msec = - 100 * 1000

    def match_no_cache(self, context):
        frame = context['engine']['frame']

        for mask in self._masks:
            matched = mask.match(frame)

            if not matched:
                return False
        return True

    def _analyze(self, context):
        pass

    def _init_scene(self, debug=False):
        self._masks = [
            IkaMatcher(
                589, 109, y0, y1 - y0,
                img_file='v2_game_timer_icon.png',
                threshold=0.9,
                orig_threshold=1.0,
                bg_method=matcher.MM_DARK(),
                fg_method=matcher.MM_DARK(),
                label='timer_icon_top',
                debug=True,
            ),

            IkaMatcher(
                589, 109, y2, y3 - y2,
                img_file='v2_game_timer_icon.png',
                threshold=0.9,
                orig_threshold=1.0,
                bg_method=matcher.MM_DARK(),
                fg_method=matcher.MM_DARK(),
                label='timer_icon_bottom',
                debug=True,
            ),

            TimerReader(),
        ]


if __name__ == "__main__":
    V2GameTimerIcon.main_func()
