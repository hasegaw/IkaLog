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

import sys

import cv2
import numpy as np

from ikalog.utils import *
from ikalog.scenes.scene import Scene


class GameOutOfBound(Scene):

    def reset(self):
        super(GameOutOfBound, self).reset()

        self._last_event_msec = - 100 * 1000

    def match_no_cache(self, context):
        if self.matched_in(context, 5 * 1000):
            return False

        if self.is_another_scene_matched(context, 'GameTimerIcon'):
            return False

        if not self.find_scene_object('GameTimerIcon').matched_in(context, 1.5 * 1000):
            return False

        frame = context['engine']['frame']

        total = np.sum(frame)
        # print('oob score=', total)

        match = total < (1280 * 720 * 3 * 16)
        if match:
            most_possible_id = 'oob'

            context['game']['last_death_reason'] = most_possible_id
            context['game']['death_reasons'][most_possible_id] = \
                context['game']['death_reasons'].get(most_possible_id, 0) + 1

            self._call_plugins('on_game_dead')
            self._call_plugins('on_game_death_reason_identified')
            return True

        return False

    def _analyze(self, context):
        pass

    def _init_scene(self, debug=False):
        pass

if __name__ == "__main__":
    GameGoSign.main_func()
