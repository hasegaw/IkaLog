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

from ikalog.utils import *
from ikalog.scenes.scene import Scene


class GameGoSign(Scene):

    def reset(self):
        super(GameGoSign, self).reset()

        self._last_event_msec = - 100 * 1000

    def match_no_cache(self, context):
        if not self.is_another_scene_matched(context, 'GameTimerIcon'):
            return False

        frame = context['engine']['frame']

        matched = self.mask_go_sign.match(frame)

        if not matched:
            return False

        if not self.matched_in(context, 60 * 1000, attr='_last_event_msec'):
            self._call_plugins('on_game_go_sign')
            self._last_event_msec = context['engine']['msec']

        return matched

    def _analyze(self, context):
        pass

    def _init_scene(self, debug=False):
        self.mask_go_sign = IkaMatcher(
            472, 140, 332, 139,
            img_file='masks/ui_go.png',
            threshold=0.90,
            orig_threshold=0.5,
            label='Go!',
            bg_method=matcher.MM_WHITE(sat=(32, 255), visibility=(0, 210)),
            fg_method=matcher.MM_WHITE(),
            debug=debug,
        )

if __name__ == "__main__":
    GameGoSign.main_func()
