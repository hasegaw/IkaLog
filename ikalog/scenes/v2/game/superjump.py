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


class V2GameSuperJump(StatefulScene):

    def reset(self):
        super(V2GameSuperJump, self).reset()

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
                return False
        return True

    def _analyze(self, context):
        pass

    def _init_scene(self, debug=False):
        self._masks = [
            IkaMatcher(
                32, 344, 50, 50,
                img_file='v2_game_superjump.png',
                bg_method=matcher.MM_DARK(),
                fg_method=matcher.MM_WHITE(),
                threshold=0.8,
                orig_threshold=0.4,
                label='superjump_left',
                debug=debug,
            ),

            IkaMatcher(
                977, 344, 50, 50,
                img_file='v2_game_superjump.png',
                bg_method=matcher.MM_DARK(),
                fg_method=matcher.MM_WHITE(),
                threshold=0.8,
                orig_threshold=0.4,
                label='superjump_right',
                debug=debug,
            ),

            IkaMatcher(
                509, 36, 50, 50,
                img_file='v2_game_superjump.png',
                bg_method=matcher.MM_DARK(),
                fg_method=matcher.MM_WHITE(),
                threshold=0.8,
                orig_threshold=0.4,
                label='superjump_top',
                debug=debug,
            ),

            IkaMatcher(
                506, 654, 267, 48,
                img_file='v2_game_superjump.png',
                bg_method=matcher.MM_DARK(),
                fg_method=matcher.MM_WHITE(),
                threshold=0.8,
                orig_threshold=0.4,
                label='superjump_top',
                debug=debug,
            ),
        ]

if __name__ == "__main__":
    V2GameSuperJump.main_func()
