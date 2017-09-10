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


class Spl2GameSubWeapon(Scene):

    def reset(self):
        super(Spl2GameSubWeapon, self).reset()

        self._last_event_msec = - 100 * 1000


    def match_no_cache(self, context):
        # pass matching in some scenes.
        in_game = self.find_scene_object('Spl2InGame')
        if in_game is not None:
            if not in_game.match(context):
                return None

        frame = context['engine']['frame']

        if frame is None:
            return None

        subweapon_key = self._c.predict_frame(context['engine']['frame'])

        return subweapon_key

    def dump(self, context):
        pass

    def _analyze(self, context):
        pass

    def _init_scene(self, debug=False):
        self._c = ImageClassifier(object)
        self._c.load_from_file('data/spl2/spl2.game.sub_weapon.dat')


if __name__ == "__main__":
    Spl2GameSubWeapon.main_func()
