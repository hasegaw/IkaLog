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

from ikalog.scenes.scene import Scene
from ikalog.utils import *


class GameTimerIcon(Scene):
    timer_left = 60
    timer_width = 28
    timer_top = 28
    timer_height = 34

    def match_no_cache(self, context):
        frame = context['engine']['frame']

        if frame is None:
            return False

        return self.mask_timer.match(frame)

    def _analyze(self, context):
        pass

    def _init_scene(self, debug=False):
        self.mask_timer = IkaMatcher(
            self.timer_left, self.timer_top, self.timer_top, self.timer_height,
            img_file='game_timer_icon.png',
            threshold=0.9,
            orig_threshold=0.35,
            bg_method=matcher.MM_BLACK(visibility=(0, 32)),
            fg_method=matcher.MM_WHITE(visibility=(160, 256)),
            label='timer_icon',
            debug=debug,
        )

if __name__ == "__main__":
    GameTimerIcon.main_func()
