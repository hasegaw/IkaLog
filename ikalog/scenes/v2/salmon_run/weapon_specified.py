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
from ikalog.ml.classifier import ImageClassifier
from ikalog.utils import *


class Spl2SalmonRunWeaponSpecified(StatefulScene):

    def reset(self):
        super(Spl2SalmonRunWeaponSpecified, self).reset()

        self._last_event_msec = - 100 * 1000
        self._cause_of_death_votes = {}

    def _state_default(self, context):
        if not self.find_scene_object('Spl2SalmonRunSession').matched_in(context, 20 * 1000):
            return False

        frame = context['engine']['frame']

        if frame is None:
            return False

        matched = self._c.predict_frame(context['engine']['frame']) > 0

        if matched:
            self._call_plugins('on_salmonrun_game_weapon_specified')
            self._switch_state(self._state_tracking)

        return matched

    def _state_tracking(self, context):
        frame = context['engine']['frame']

        if frame is None:
            return False

        matched = self._c.predict_frame(context['engine']['frame']) > 0

        # 画面が続いているならそのまま
        if matched:
            return True

        # 1000ms 以内の非マッチはチャタリングとみなす
        if not matched and self.matched_in(context, 1000):
            return False

        #self._last_event_msec = context['engine']['msec']
        self._switch_state(self._state_default)

        return False

    def dump(self, context):
        pass

    def _analyze(self, context):
        pass

    def _init_scene(self, debug=False):
        self._c = ImageClassifier()
        self._c.load_from_file(
            'data/spl2/spl2.salmon_run.game.weapon_change.dat')


if __name__ == "__main__":
    Spl2SalmonRunWeaponSpecified.main_func()
