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


class SalmonRunGameOver(StatefulScene):

    def reset(self):
        super(SalmonRunGameOver, self).reset()

        self._last_event_msec = - 100 * 1000

    def _get_state_from_frame(self, context):
        frame = context['engine']['frame']
        r = self._c.predict_frame(context['engine']['frame'])

        return r >= 0

    def _state_default(self, context):
        matched = self._get_state_from_frame(context)

        if matched:
            self._call_plugins('on_salmonrun_game_over')
            self._switch_state(self._state_work_over)

        return matched

    def _state_work_over(self, context):
        matched = self._get_state_from_frame(context)

        if matched:
            return True

        return self.check_timeout(context)

    def check_timeout(self, context):
        # 5000ms 以内の非マッチはチャタリングとみなす
        if self.matched_in(context, 5000):
            return False

        self._last_event_msec = context['engine']['msec']
        self._switch_state(self._state_default)
        return False

    def dump(self, context):
        pass

    def _analyze(self, context):
        pass

    def _init_scene(self, debug=False):
        self._c = ImageClassifier()
        self._c.load_from_file('spl2.salmon_run.game.over.dat')


if __name__ == "__main__":
    SalmonRunGameOver.main_func()
