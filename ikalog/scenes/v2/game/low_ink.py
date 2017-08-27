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

from ikalog.ml.classifier import ImageClassifier
from ikalog.scenes.scene import Scene
from ikalog.utils import *


class Spl2GameLowInk(Scene):

    def reset(self):
        super(Spl2GameLowInk, self).reset()

        self._last_event_msec = - 100 * 1000

    def match_no_cache(self, context):
        # pass matching in some scenes.
        session = self.find_scene_object('Spl2GameSession')
        if session is not None:
            if not (session._state.__name__ in ('_state_battle')):
                return False

        frame = context['engine']['frame']

        if frame is None:
            return False

        matched = self._c.predict_frame(context['engine']['frame']) >= 0

        if matched and self._last_event_msec + 3000 < context['engine']['msec']:
            context['game']['low_ink_count'] = \
                context['game'].get('low_ink_count', 0) + 1
            self._last_event_msec = context['engine']['msec']

            self._call_plugins('on_game_low_ink')

        return matched

    def dump(self, context):
        pass

    def _analyze(self, context):
        pass

    def _init_scene(self, debug=False):
        self._c = ImageClassifier(object)
        self._c.load_from_file('data/spl2/spl2.game.low_ink.dat')


if __name__ == "__main__":
    Spl2GameLowInk.main_func()
