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
from ikalog.utils import *


class V2GameSession(StatefulScene):

    def reset(self):
        super(V2GameSession, self).reset()

        self._last_event_msec = - 100 * 1000

    def _state_default(self, context):
        in_battle = \
            self.is_another_scene_matched(context, 'GameTimerIcon') or \
            self.is_another_scene_matched(context, 'V2GameSuperjump')

        if in_battle:
            self._switch_state(self._state_battle)

    def _state_battle(self, context):
        in_battle = \
            self.is_another_scene_matched(context, 'GameTimerIcon') or \
            self.is_another_scene_matched(context, 'V2GameSuperjump')

        if not in_battle:
            self._switch_state(self._state_default)

    def _analyze(self, context):
        pass

    def _init_scene(self, debug=False):
        pass


if __name__ == "__main__":
    V2GameSession.main_func()
