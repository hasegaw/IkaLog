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

from ikalog.scenes.scene import Scene
from ikalog.utils import *

from ikalog.ml.classifier import ImageClassifier


class Spl2InGame(Scene):

    def reset(self):
        super(Spl2InGame, self).reset()

        self._last_event_msec = - 100 * 1000

    def match_no_cache(self, context):
        matched = self._c_ingame.predict_frame(context['engine']['frame']) >= 0
        return matched

    def _analyze(self, context):
        pass

    def _init_scene(self, debug=False):
        self._c_ingame = ImageClassifier()
        self._c_ingame.load_from_file('data/spl2.game.in_game.dat')


if __name__ == "__main__":
    Spl2InGame.main_func()
