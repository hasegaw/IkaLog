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

from ikalog.ml.classifier import ImageClassifier


class Spl2GameMap(StatefulScene):

    def reset(self):
        super(Spl2GameMap, self).reset()

        self._last_event_msec = - 100 * 1000

    def _state_default(self, context):
        matched = self._c_start.predict_frame(context['engine']['frame']) >= 0

        if matched:
            self._switch_state(self._state_tracking)
            self._call_plugins('on_game_map_open')

        return matched

    def _state_tracking(self, context):
        matched = self._c_start.predict_frame(context['engine']['frame']) >= 0

        # Exit the scene if it doesn't matched for 1000ms
        if (not matched) and (not self.matched_in(context, 1000)):
            self._switch_state(self._state_default)
            self._call_plugins('on_game_map_close')

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
        self._c_start = ImageClassifier()
        self._c_start.load_from_file('data/spl2/spl2.game_map.dat')


if __name__ == "__main__":
    Spl2GameMap.main_func()
