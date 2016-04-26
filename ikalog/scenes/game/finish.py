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


class GameFinish(Scene):

    def reset(self):
        super(GameFinish, self).reset()

        self._last_event_msec = - 100 * 1000

    def match_no_cache(self, context):
        if self.matched_in(context, 60 * 1000, attr='_last_event_msec'):
            return False

        if self.is_another_scene_matched(context, 'GameTimerIcon'):
            return False

        if not self.find_scene_object('GameTimerIcon').matched_in(context, 20 * 1000):
            return False

        frame = context['engine']['frame']

        if not self.mask_finish.match(frame):
            return False

        self._call_plugins('on_game_finish')
        self._last_event_msec = context['engine']['msec']

        return True

    def _analyze(self, context):
        pass

    def _init_scene(self, debug=False):
        self.mask_finish = IkaMatcher(
            0, 0, 1280, 720,
            img_file='game_finish.png',
            threshold=0.90,
            orig_threshold=0.20,
            bg_method=matcher.MM_BLACK(),
            fg_method=matcher.MM_NOT_BLACK(),
            label='Finish',
            debug=debug,
        )

if __name__ == "__main__":
    GameFinish.main_func()
