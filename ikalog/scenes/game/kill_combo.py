#!/usr/bin/env python3
# -*- coding: utf-8 -*-
#
#  IkaLog
#  ======
#  Copyright (C) 2015 Takeshi HASEGAWA, Shingo MINAMIYAMA
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

from ikalog.scenes.scene import Scene
from ikalog.utils import *

class GameKillCombo(Scene):

    def reset(self):
        super(GameKillCombo, self).reset()
        self.resetParams()
        self.max_kill_streak = 0
        self.max_kill_combo = 0

    def resetParams(self):
        self.chain_kill_combos = 0
        self.kill_streak = 0
        self.last_kill_msec = 0

    def match_no_cache(self, context):
        if not self.is_another_scene_matched(context, 'GameTimerIcon'):
            return False

        frame = context['engine']['frame']

        if frame is None:
            return False

    def on_game_killed(self, context, params):
        self.kill_streak += 1
        context['game']['kill_streak'] = self.kill_streak
        context['game']['max_kill_streak'] = max(self.kill_streak, context['game'].get('max_kill_streak', 0))

        if (self.kill_streak > 1 and (context['engine']['msec'] - self.last_kill_msec) <= 5000):
            self.chain_kill_combos += 1
            context['game']['kill_combo'] = self.chain_kill_combos
            context['game']['max_kill_combo'] = max(self.chain_kill_combos, context['game'].get('max_kill_combo', 0))

            self._call_plugins('on_game_chained_kill_combo')
        else:
            self.chain_kill_combos = 1; 
            context['game']['kill_combo'] = self.chain_kill_combos 
            context['game']['max_kill_combo'] = max(self.chain_kill_combos, context['game'].get('max_kill_combo', 0)) 

        self.last_kill_msec = context['engine']['msec']

    def on_game_dead(self, context):
        self.resetParams()

    def on_game_reset(self, context):
        self.resetParams()
        self.max_kill_streak = 0
        self.max_kill_combo = 0

    def _analyze(self, context):
        pass

    def _init_scene(self, debug=False):
        pass

if __name__ == "__main__":
    GameKillCombo.main_func()
