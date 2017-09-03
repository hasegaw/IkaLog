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


class Spl2SalmonRunMrGrizz(StatefulScene):

    def reset(self):
        super(Spl2SalmonRunMrGrizz, self).reset()

        self._last_event_msec = - 100 * 1000
        self._last_message = None
        self._switch_state(self._state_default)

    def _state_default(self, context):
        frame = context['engine']['frame']
        r = self._c_text.predict_frame(context['engine']['frame'])
        if r != -1:
            self._last_message = r
            # Mr.Grizz'scomment
            self._call_plugins(
                'on_salmonrun_mr_grizz_comment', params={'text_id': r})
            self._switch_state(self._state_tracking)

    def _state_tracking(self, context):
        r = self._c_text.predict_frame(context['engine']['frame'])
        if r == self._last_message:
            return True
        if r != self._last_message:
            self._switch_state(self._state_default)
            return True

        return self.check_timeout(context)

    def check_timeout(self, context):
        # 1000ms 以内の非マッチはチャタリングとみなす
        if self.matched_in(context, 1000):
            return False

        self._switch_state(self._state_default)
        return False

    def dump(self, context):
        pass

    def _analyze(self, context):
        pass

    def _init_scene(self, debug=False):
        self._c_text = ImageClassifier()
        self._c_text.load_from_file('data/spl2/spl2.salmon_run.mr_grizz.dat')

        self._disable_state_message = False


if __name__ == "__main__":
    Spl2SalmonRunMrGrizz.main_func()
