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


class V2GameRespawn(StatefulScene):

    def reset(self):
        super(V2GameRespawn, self).reset()

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
        if (not matched) and (not self.matched_in(context, 100)):
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
                567, 561, 191, 62,
                img_file='v2_game_respawn.png',
                bg_method=matcher.MM_NOT_WHITE(),
                fg_method=matcher.MM_WHITE(),
                threshold=0.83,
                orig_threshold=0.1,
                label='game_respawn',
                debug=False,
            ),
        ]

if __name__ == "__main__":
    V2GameRespawn.main_func()
