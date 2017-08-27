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


def get_salmonrun_from_context(context):
    if not 'salmon_run' in context:
        context['salmon_run'] = {}
    return context['salmon_run']


class Spl2SalmonRunResultJudge(StatefulScene):

    def reset(self):
        super(Spl2SalmonRunResultJudge, self).reset()

        self._last_event_msec = - 100 * 1000

    def _get_result_from_frame(self, context):
        frame = context['engine']['frame']
        r = self._c.predict_frame(context['engine']['frame'])

        return {0: 'clear', 1: 'failure', -1: None}.get(r)

    def _state_default(self, context):
        result = self._get_result_from_frame(context)

        if result is not None:
            ctx_salmonrun = get_salmonrun_from_context(context)
            ctx_salmonrun['result'] = result
            self._call_plugins('on_salmonrun_result_judge')
            self._switch_state(self._state_tracking)
            return True

        return False

    def _state_tracking(self, context):
        result = self._get_result_from_frame(context)

        if result is None:
            return self.check_timeout(context)

        return True

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
        self._c.load_from_file('data/spl2/spl2.salmon_run.result.judge.dat')


if __name__ == "__main__":
    ResultJudge.main_func()
