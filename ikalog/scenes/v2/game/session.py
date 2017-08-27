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


class Spl2GameSession(StatefulScene):
    def reset(self):
        super(Spl2GameSession, self).reset()
        self._grace_period = 5000

    def check_timeout(self, context):
        if self._state == self._state_default:
            return False

        grace_period = self._grace_periods[self._state.__name__]
        timeout = self.matched_in(context, grace_period)
        return timeout

        self._grace_period = 6000

    def on_game_start(self, context):
        self._switch_state(self._state_game_start)
        self._set_matched(context)

    def _state_default(self, context):
        in_battle = \
            self.is_another_scene_matched(context, 'Spl2InGame') or \
            self.is_another_scene_matched(context, 'V2GameSuperjump')

        if in_battle:
            self._switch_state(self._state_battle)
        return in_battle

    def _state_game_start(self, context):
        in_battle = \
            self.is_another_scene_matched(context, 'Spl2InGame') or \
            self.is_another_scene_matched(context, 'V2GameSuperjump')

        if in_battle:
            self._switch_state(self._state_battle)
            context['game']['splatoon_edition'] = 'spl2'

        if not in_battle and self.check_timeout(context):
            self._switch_state(self._state_default)

        return in_battle

    def _state_battle(self, context):
        in_battle = \
            self.is_another_scene_matched(context, 'Spl2InGame') or \
            self.is_another_scene_matched(context, 'V2GameSuperjump')

        if in_battle:
            self._set_matched(context)

        if not in_battle and self.check_timeout(context):
            self._switch_state(self._state_default)

        return in_battle

    def _state_battle_finished(self, context):
        if self.is_another_scene_matched(context, 'Spl2BattleFinish'):
            return True

        if self.check_timeout(context):
            self._switch_state(self._state_default)

    def _analyze(self, context):
        pass

    def _init_scene(self, debug=False):
        self._grace_periods = {
            '_default': 0,
            '_state_battle': 6000,
            '_state_game_start': 20000,
            '_state_battle_finished': 10000,
        }


if __name__ == "__main__":
    Spl2GameSession.main_func()
