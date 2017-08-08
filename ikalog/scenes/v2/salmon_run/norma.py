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


class SalmonRunNorma(StatefulScene):

    def reset(self):
        super(SalmonRunNorma, self).reset()

        self._last_event_msec = - 100 * 1000
        self._cause_of_death_votes = {}

    def _get_state_from_frame(self, context):
        frame = context['engine']['frame']
        r = self._c.predict1_multiclass(
            self._c.extract_rect(context['engine']['frame']))[0][0]

        return {0: self._state_norma_not_reached, 1: self._state_norma_reached, -1: self._state_default}.get(r)

    def _state_default(self, context):
        new_state = self._get_state_from_frame(context)

        if new_state == self._state_norma_not_reached:
            self._switch_state(self._state_norma_not_reached)

        if new_state == self._state_norma_reached:
            self._switch_state(self._state_norma_reached)

        return new_state != self._state_default

    def _state_norma_not_reached(self, context):
        new_state = self._get_state_from_frame(context)

        if new_state == self._state_norma_not_reached:
            return True

        if new_state == self._state_norma_reached:
            self._call_plugins('on_salmonrun_norma_reached')
            self._switch_state(self._state_norma_reached)
            return True

        return self.check_timeout(context)

    def _state_norma_reached(self, context):
        new_state = self._get_state_from_frame(context)

        if new_state == self._state_norma_reached:
            return True

        if new_state == self._state_norma_not_reached:
            self._switch_state(self._state_norma_not_reached)
            return True

        return self.check_timeout(context)

    def check_timeout(self, context):
        # 3000ms 以内の非マッチはチャタリングとみなす
        if self.matched_in(context, 3000):
            return False

        self._last_event_msec = context['engine']['msec']
        self._switch_state(self._state_default)
        print('%s: force default state')
        return False

    def dump(self, context):
        pass

    def _analyze(self, context):
        pass

    def _init_scene(self, debug=False):
        self._c = ImageClassifier()
        self._c.load_from_file('spl2.salmon_run.game.norma.dat')


if __name__ == "__main__":
    SalmonRunNorma.main_func()
