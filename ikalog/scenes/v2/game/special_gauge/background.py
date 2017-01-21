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

import sys

import cv2

from ikalog.scenes.stateful_scene import StatefulScene
from ikalog.utils import *


class V2GameSpecialGaugeBackground(StatefulScene):

    def reset(self):
        super(V2GameSpecialGaugeBackground, self).reset()

        self._last_event_msec = - 100 * 1000

    def _state_default(self, context):
        matched = self.match1(context)

        if matched:
            self._switch_state(self._state_tracking)
            return True

        return False

    def _state_tracking(self, context):
        matched = self.match1(context)

        # Exit the scene if it doesn't matched for 1000ms
        if (not matched) and (not self.matched_in(context, 1000)):
            self._switch_state(self._state_default)

        return matched

    def match1(self, context):
        frame = context['engine']['frame']

        for mask in self._masks:
            matched = mask.match(frame)

            if not matched:
                #print(self, matched)
                return False
        #print(self, matched)
        return True

    def _analyze(self, context):
        pass

    def _init_scene(self, debug=False):
        self._masks = [
            IkaMatcher(
                1166,17, 83,67,
                img_file='v2_game_special_gauge.png',
                bg_method=matcher.MM_DARK(visibility=(0, 255)),
                fg_method=matcher.MM_DARK(),
                threshold=0.8,
                orig_threshold=0.4,
                label='game_special_gauge',
                debug=debug,
            ),

            IkaMatcher(
                1127, 63, 29, 35,
                img_file='v2_game_special_gauge.png',
                bg_method=matcher.MM_DARK(visibility=(0, 255)),
                fg_method=matcher.MM_DARK(),
                threshold=0.8,
                orig_threshold=0.4,
                label='game_special_gauge_2',
                debug=debug,
            ),
        ]

if __name__ == "__main__":
    V2GameSpecialGaugeBackground.main_func()
