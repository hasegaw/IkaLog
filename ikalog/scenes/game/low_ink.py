#!/usr/bin/env python3
# -*- coding: utf-8 -*-
#
#  IkaLog
#  ======
#  Copyright (C) 2016 Takeshi HASEGAWA
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


class GameLowInk(Scene):

    def reset(self):
        super(GameLowInk, self).reset()

        self._last_event_msec = - 100 * 1000

    def match_no_cache(self, context):
        # It should be ok
        if not self.is_another_scene_matched(context, 'GameTimerIcon'):
            return False

        frame = context['engine']['frame']

        if frame is None:
            return False

        matched = self.mask_low_ink.match(context['engine']['frame'])

        if matched and self._last_event_msec + 3000 < context['engine']['msec']:
            context['game']['low_ink_count'] = \
                context['game'].get('low_ink_count', 0) + 1
            self._last_event_msec = context['engine']['msec']

            self._call_plugins('on_game_low_ink')

        return matched

    def dump(self, context):
        print('low_ink %s' % context['game']['death_reasons'])

    def _analyze(self, context):
        pass

    def _init_scene(self, debug=False):
        self.mask_low_ink = IkaMatcher(
            597, 530, 118, 41,
            img_file='game_low_ink.png',
            threshold=0.98,
            orig_threshold=0.2,

            bg_method=matcher.MM_DARK(visibility=(0, 160)),
            fg_method=matcher.MM_WHITE(),
            label='game/low_ink',
            call_plugins=self._call_plugins,
            debug=debug,
        )

if __name__ == "__main__":
    GameLowInk.main_func()
