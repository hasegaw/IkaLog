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

import copy
import cv2
import numpy as np

from ikalog.scenes.stateful_scene import StatefulScene
from ikalog.utils import *


class V2ResultScoreboard(StatefulScene):

    def reset(self):
        super(V2ResultScoreboard, self).reset()

        self._last_img_bar_b_i16 = None
        self._last_event_msec = - 100 * 1000

    def _state_default(self, context):
        frame = context['engine']['frame']

        if frame is None:
            return False

        matched = self.match1(context)
        if not matched:
            return False

        cv2.imshow('gathered2', context['engine']['frame'])
        self._switch_state(self._state_tracking)
        self._last_matched_msec = context['engine']['msec']

        return True

    def _state_tracking(self, context):
        frame = context['engine']['frame']

        if frame is None:
            return False

        matched = self.match1(context)
        if matched:
            self._last_matched_msec = context['engine']['msec']
            return True

        # Exit the scene if it doesn't matched for 1000ms
        if (not matched) and (not self.matched_in(context, 1000)):
            self._switch_state(self._state_default)

        if self.matched_in(context, 30 * 1000, attr='_last_event_msec'):
            return matched

        triggered = self.match_still(context)
        if triggered:
            self._analyze(context)
            self._call_plugins('on_result_scoreboard')
            self._last_event_msec = context['engine']['msec']

        return matched
   
    def match1(self, context):
        frame = context['engine']['frame']

        for mask in self._masks:
            matched = mask.match(frame)

            if not matched:
                return False
        return True


    def match_still(self, context):
        img_bar = context['engine']['frame'][573:573+125, :, :]
        img_bar_b = image_filters.MM_WHITE()(img_bar)
        img_bar_b_i16 = np.array(img_bar_b, dtype=np.int16)

        if self._last_img_bar_b_i16 is None:
            self._last_img_bar_b_i16 = img_bar_b_i16
            return False

        img_diff = abs(img_bar_b_i16 - self._last_img_bar_b_i16)
        self._last_img_bar_b_i16 = img_bar_b_i16

        loss = np.sum(img_diff) / 255
        threshold = img_diff.shape[0] * img_diff.shape[1] * 0.001

        return loss < threshold


    def _analyze(self, context):
        pass


    def dump(self, context):
        pass

    def _init_scene(self, debug=False):
        self._masks = [
            IkaMatcher(
                680, 33, 156, 93,
                img_file='v2_result_scoreboard.png',
                bg_method=matcher.MM_BLACK(),
                fg_method=matcher.MM_NOT_BLACK(),
                threshold=0.8,
                orig_threshold=0.4,
                label='scoreboard:win',
                debug=debug,
            ),

            IkaMatcher(
                680, 360, 156, 93,
                img_file='v2_result_scoreboard.png',
                bg_method=matcher.MM_BLACK(),
                fg_method=matcher.MM_NOT_BLACK(),
                threshold=0.8,
                orig_threshold=0.4,
                label='scoreboard:lose',
                debug=debug,
            ),
        ]


if __name__ == "__main__":
    V2ResultScoreboard.main_func()
