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


class Blank(Scene):

    def reset(self):
        super(Blank, self).reset()

        self._last_event_msec = - 100 * 1000


    def _is_black(self, img):
        maxval = img.shape[0] * img.shape[1] * img.shape[2]
        score  = np.sum(img)
        return score < maxval * 16

    def match_no_cache(self, context):
        if self.matched_in(context, 5 * 1000):
            return False

        if self.is_another_scene_matched(context, 'GameTimerIcon'):
            return False

        frame = context['engine']['frame']

        matched = \
            self._is_black(frame[230:230 + 350, :, :]) and \
            self._is_black(frame[230 + 150:, :frame.shape[1] - 190, :])

        return matched

    def _analyze(self, context):
        pass

    def _init_scene(self, debug=False):
        pass

if __name__ == "__main__":
    Blank.main_func()
