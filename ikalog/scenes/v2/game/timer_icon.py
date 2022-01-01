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

from ikalog.scenes.stateful_scene import StatefulScene
from ikalog.ml.text_reader import TextReader
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
y1 = 16 + 22
y2 = 16 + 48
y3 = 16 + 72


class TimerReader(object):
    _p_threshold = 0.7
    time_regexp = re.compile('(\d+):(\d+)')

    def _read_time(self, img):
        # if self._debug:
        cv2.imwrite('time.png', img)

        img = cv2.resize(img, (img.shape[1] * 2, img.shape[0] * 2))

        img_hsv = cv2.cvtColor(img, cv2.COLOR_BGR2HSV)
        img_gray = img_hsv[:, :, 2]
        img_gray[img_gray < 210] = 0
        img_gray[img_hsv[:, :, 1] > 30] = 0
        img_gray[img_gray > 0] = 255

        val_str = None
        val_str = self._number_recoginizer.read_char(img_gray)
        if self._debug:
            print('Read: %s' % val_str)

        return val_str

    def read_time(self, img):
        img = cv2.cvtColor(img, cv2.COLOR_GRAY2BGR)
        timestr = self._read_time(img)

        if not timestr:
            return False

        result = re.match(self.time_regexp, timestr)
        if not result:
            return False
        m = int(result.group(1))
        s = int(result.group(2))

        valid = (m <= 5) and (s <= 59)

        if valid:
            self._time_remaining = m * 60 + s

        return valid

    def match(self, img):
        img_timestr = img[y1: y2, 610:610 + 60]

        img_timer_black = matcher.MM_BLACK()(img_timestr)
        img_timer_white = matcher.MM_WHITE()(img_timestr)
        # img_timer_yellow = matcher.MM_COLOR_BY_HUE(
        #     hue=(27 - 5, 27 + 5), visibility=(100, 255))(img_timestr)

        img_test = img_timer_black | img_timer_white # | img_timer_yellow
        orig_hist = cv2.calcHist([img_test], [0], None, [2], [0, 256])
        self._p = (orig_hist[1] / (orig_hist[0] + orig_hist[1]))

        time_valid = False
        if True or self._p > self._p_threshold:
            time_valid = self.read_time(255 - img_timer_black)

        return time_valid
        # return self.read_time(255 - img_timer_black)

    def __init__(self, debug=False):
        self._debug = debug
        self._time_remaining = 0
        self._number_recoginizer = TextReader()

    def get_time(self):
        return self._time_remaining


class GameTimerIcon(StatefulScene):

    def reset(self):
        super(GameTimerIcon, self).reset()

        self._last_event_msec = - 100 * 1000


    def _state_default(self, context):
        session = self.find_scene_object('Spl2GameSession')
        if session is not None:
            is_start = session._state.__name__ in ('_state_game_start', 'Spl2GameSession')
            if not (is_start):
                return False
        matched = self.check_match(context)

        if matched:
            self._switch_state(self._state_tracking)
            # Set the team colors on first match
            # TODO Alecat - decide on this method vs team_color detection in start.py
            frame = context['engine']['frame']
            if 'game' in context and 'team_color_rgb' not in context['game']:
                context['game']['team_color_rgb'] = [
                    (int(frame[68][565][2]), int(frame[68][565][1]), int(frame[68][565][0])),
                    (int(frame[68][730][2]), int(frame[68][730][1]), int(frame[68][730][0])),
                ]

    def _state_tracking(self, context):
        frame = context['engine']['frame']

        session = self.find_scene_object('Spl2GameSession')
        if session is not None:
            has_started = session._state.__name__ in ('_state_game_start', 'Spl2GameSession')
            if not has_started:
                return False

        matched = self.check_match(context)
        escaped = not self.matched_in(context, 1000)

        if escaped:
            self._switch_state(self._state_default)
        if matched:
            if self._mask_overtime.match(frame):
                self._overtime = True
        
        return matched

    def check_match(self, context):
        frame = context['engine']['frame']

        for mask in self._masks:
            matched = mask.match(frame)

            if not matched:
                return False

        # if not self._timer_reader.match(frame):
        #     return False
        

        # print("TIMER VS GAME", 300 - self._timer_reader.get_time(), context['engine'].get('msec'), context['game'].get('start_offset_msec'), context['engine'].get('msec') - context['game'].get('start_offset_msec'))

        return True

    def _analyze(self, context):
        pass

    def dump(self, context):
        super(GameTimerIcon, self).dump(context)
        print('--------')
        # print(self._overtime)
        # print(self._timer_reader.get_time())

    def _init_scene(self, debug=False):
        self._overtime = False

        self.perfect_mask = IkaMatcher(
            589, y0, 109, y3 - y0,
            img_file='v2_game_timer_icon.png',
            threshold=0.95,
            orig_threshold=1.0,
            bg_method=matcher.MM_DARK(),
            fg_method=matcher.MM_BLACK(),
            label='timer_icon_top',
            debug=debug,
        )
        self._masks = [
            IkaMatcher(
                589, y0, 109, y1 - y0,
                img_file='v2_game_timer_icon.png',
                threshold=0.95,
                orig_threshold=1.0,
                bg_method=matcher.MM_DARK(),
                fg_method=matcher.MM_BLACK(),
                label='timer_icon_top',
                debug=debug,
            ),

            IkaMatcher(
                589, y2, 109, y3 - y2,
                img_file='v2_game_timer_icon.png',
                threshold=0.95,
                orig_threshold=1.0,
                bg_method=matcher.MM_DARK(),
                fg_method=matcher.MM_BLACK(),
                label='timer_icon_bottom',
                debug=debug,
            ),
        ]
        self._mask_overtime = IkaMatcher(
                585, y1, 109, y2 - y1,
                img_file='v2_game_timer_overtime.png',
                threshold=0.95,
                orig_threshold=1.0,
                bg_method=matcher.MM_BLACK(visibility=(0, 100)),
                fg_method=matcher.MM_COLOR_BY_HUE(
                    hue=(10 - 5, 10 + 5), visibility=(100, 255)),
                label='timer_overtime',
                debug=debug,
            )
        # self._timer_reader = TimerReader(debug=debug)



if __name__ == "__main__":
    GameTimerIcon.main_func()
