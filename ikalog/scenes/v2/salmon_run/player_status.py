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
import time

import cv2

from ikalog.scenes.stateful_scene import StatefulScene
from ikalog.ml.classifier import ImageClassifier
from ikalog.utils import *


class Spl2SalmonRunPlayerStatus(StatefulScene):

    def reset(self):
        super(Spl2SalmonRunPlayerStatus, self).reset()

        self._last_event_msec = - 100 * 1000

    def on_salmonrun_wave_start(self, context, params):
        self.reset()

    def _extract_player_state(self, context):
        frame = context['engine']['frame']

        players = []

        x_list = [47, 95, 95 + 48, 95 + 48 + 48]
        for x in x_list:
            p = frame[127:127 + 39, x:x + 24]

            r_egg = self._c_egg.predict1(p) == 0
            r_dead = self._c_dead.predict1(p) == 0

            players.append({'active': not r_dead, 'has_egg': r_egg})

            if 0:
                filename = 'spl2.salmon_run.player_status.%s%s_%s.png' % (
                    egg, dead, time.time())
                w = '%s%s' % (egg, dead)
                cv2.imshow(w, p1)
                #cv2.imwrite('spl2.salmon_run.player_status.%s.png' % time.time(), p1)
        return players

    def _get_state_from_frame(self, context):
        last_players = context['game'].get(
            'salmon_run_players', [{}, {}, {}, {}])
        players = self._extract_player_state(context)
        index = range(4)

        for last_player, player, i in zip(last_players, players, index):
            last_active = last_player.get('active', player.get('active'))
            last_has_egg = last_player.get('has_egg', player.get('has_egg'))

            if player.get('has_egg') != last_has_egg:
                if last_has_egg:
                    self._call_plugins('on_salmonrun_egg_delivered', params={'player': i})
                else:
                    self._call_plugins('on_salmonrun_egg_captured', params={'player': i})
            if player.get('active') != last_active:
                if last_active:
                    self._call_plugins('on_salmonrun_player_dead', params={'player': i})
                else:
                    self._call_plugins('on_salmonrun_player_back', params={'player': i})

        context['game']['salmon_run_players'] = players

    def _state_default(self, context):
        if not self.is_another_scene_matched(context, 'Spl2SalmonRunNorma'):
            return False

        self._get_state_from_frame(context)
        return True

    def dump(self, context):
        pass

    def _analyze(self, context):
        pass

    def _init_scene(self, debug=False):
        self._c_egg = ImageClassifier()
        self._c_dead = ImageClassifier()
        self._c_egg.load_from_file('data/spl2/spl2.salmon_run.player_egg.dat')
        self._c_dead.load_from_file('data/spl2/spl2.salmon_run.player_dead.dat')


if __name__ == "__main__":
    Spl2SalmonRunPlayerStatus.main_func()
