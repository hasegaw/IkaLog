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


class GameSpecialGauge(Scene):

    def reset(self):
        super(GameSpecialGauge, self).reset()

        self._last_event_msec = - 100 * 1000

    def match_no_cache(self, context):
        if self.is_another_scene_matched(context, 'GameTimerIcon') == False:
            return False

        frame = context['engine']['frame']

        img = frame[34:34+102, 1117:1117+102]
        img_filtered = 255 - self._mm_dark.evaluate(img)
        img_masked = np.minimum(img_filtered, self._mask_gauge[:, :, 0])
        # cv2.imshow('gauge', img_masked)

        pixels = np.sum(img_masked) / 255
        value = int(pixels / self._gauge_pixels * 100)
        last_value = context['game'].get('special_gauge', None)
        if value != last_value:
            context['game']['special_gauge'] = value
            self._call_plugins('on_game_special_gauge_update')

        return False

    def _analyze(self, context):
        pass

    def _init_scene(self, debug=False):
        self._mask_gauge = np.zeros((102, 102, 3), dtype=np.uint8)
        cv2.circle(self._mask_gauge, (51, 51), 48, (255, 255, 255), 3)
        self._mask_gauge[0:55, 0:55] = np.zeros((55,55, 3), dtype=np.uint8)

        self._mm_dark = matcher.MM_DARK()
        
        self._gauge_pixels = np.sum(self._mask_gauge[:, :, 0]) / 255

if __name__ == "__main__":
    GameSpecialGauge.main_func()
