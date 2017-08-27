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


class Spl2SalmonRunSession(StatefulScene):

    def reset(self):
        super(Spl2SalmonRunSession, self).reset()
        self._last_event_msec = - 100 * 1000

    def _state_default(self, context):
        if self.is_another_scene_matched(context, 'SalmonRunStage'):
            self._switch_state(self._state_start)

        if self.is_another_scene_matched(context, 'SalmonRunNorma'):
            self._switch_state(self._state_in_work)

        return False

    def _state_in_work(self, context):
        if self.is_another_scene_matched(context, 'SalmonRunNorma'):
            return True

        return self.check_timeout(context, msec=10000)

    def _state_result(self, context):
        return self.check_timeout(context, msec=10000)

    def on_salmonrun_result_judge(self, context, args=None):
        self._switch_state(self._state_result)

    def check_timeout(self, context, msec=1000):
        if self.matched_in(context, msec):
            return False

        if self._state == self._state_in_work:
            print('%s: session abort (unexpected)' % self)
            self._call_plugins('on_salmonrun_session_abort')
        elif self._state == self._state_result:
            print('%s: session closed' % self)
            self._call_plugins('on_salmonrun_session_close')

        self._last_event_msec = context['engine']['msec']
        self._switch_state(self._state_default)
        self.reset()

        return False

    def dump(self, context):
        pass

    def _analyze(self, context):
        pass

    def _init_scene(self, debug=False):
        pass


if __name__ == "__main__":
    Spl2SalmonRunSession.main_func()
