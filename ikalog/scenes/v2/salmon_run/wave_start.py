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


class Spl2SalmonRunWaveStart(StatefulScene):

    def reset(self):
        super(Spl2SalmonRunWaveStart, self).reset()

        self._last_event_msec = - 100 * 1000
        self._current_wave = None

    def _get_state_from_frame(self, context):
        frame = context['engine']['frame']

        r = self._c.predict_frame(context['engine']['frame'])
        if r is None:
            return None
        return r + 1  # wave number

    def _state_default(self, context):
        new_wave = self._get_state_from_frame(context)

        if new_wave == 0:
            return False

        self.current_wave = new_wave
        self._call_plugins('on_salmonrun_wave_start',
                           params={'wave': new_wave})
        self._switch_state(self._state_wave_start)

        import time
        cv2.imwrite('salmon_run.wave%d.%s.png' % (new_wave, time.time()), context['engine']['frame'])

        return True

    def _state_wave_start(self, context):
        new_wave = self._get_state_from_frame(context)

        if new_wave > 0:
            return True

        return self.check_timeout(context)

    def check_timeout(self, context):
        # 3000ms 以内の非マッチはチャタリングとみなす
        if self.matched_in(context, 3000):
            return False

        self._switch_state(self._state_default)
        return False

    def dump(self, context):
        pass

    def _analyze(self, context):
        pass

    def _init_scene(self, debug=False):
        self._c = ImageClassifier()
        self._c.load_from_file('data/spl2/spl2.salmon_run.wave_start.dat')


if __name__ == "__main__":
    Spl2SalmonRunWaveStart.main_func()
