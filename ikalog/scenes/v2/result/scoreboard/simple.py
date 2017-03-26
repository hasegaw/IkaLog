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

import copy
import re
import traceback

import cv2

from ikalog.scenes.stateful_scene import StatefulScene
from ikalog.inputs.filters import OffsetFilter
from ikalog.utils import *

from ikalog.scenes.v2.result.scoreboard.extract import extract_players
from ikalog.utils.character_recoginizer.number2 import Number2Classifier
#from ikalog.utils.ikamatcher1 import IkaMatcher1


class ResultScoreboard(StatefulScene):

    def analyze(self, context):
        context['game']['players'] = []
        weapon_list = []

        return

    def reset(self):
        super(ResultScoreboard, self).reset()

        self._last_event_msec = - 100 * 1000
        self._match_start_msec = - 100 * 1000

        self._last_frame = None
        self._diff_pixels = []

    def _state_default(self, context):
        if self.matched_in(context, 30 * 1000):
            return False

        frame = context['engine']['frame']

        if frame is None:
            return False

        matched_r3 = self.mask_win.match(frame)
        if not matched_r3:
            return False

        matched_r1 = self.mask_win_hook.match(frame)
        matched_r2 = self.mask_lose_hook.match(frame)

        matched = matched_r1 and matched_r2 and matched_r3

        if matched:
            self._switch_state(self._state_tracking)

            context['game']['image_scoreboard'] = \
                copy.deepcopy(context['engine']['frame'])
            self._call_plugins_later('on_result_detail_still')

            players = extract_players(frame)
            for p in players:
                try:
                    score = self.number_recoginizer.match(p['img_score'])
                    p['score'] = re.sub(r'p$', r'', score)
                except:
                    pass

                p['kill'] = self.number_recoginizer.match_digits(p['img_kill'])
                p['death'] = self.number_recoginizer.match_digits(
                    p['img_death'])

                # backward compatibility
                p['me'] = p.get('myself')
                p['kills'] = p['kill']
                p['deaths'] = p['death']

            context['game']['players'] = players

            # won?
            me = list(filter(lambda x: x['myself'], players))[0]
            context['game']['won'] = (me['team'] == 0)

            # for debug....
            context['game']['lobby'] = 'private'

            self._call_plugins_later('on_result_detail')
            self._call_plugins_later('on_game_individual_result')

#        if matched:
#            self._match_start_msec = context['engine']['msec']
#            self._switch_state(self._state_tracking)
        return matched

    def _state_tracking(self, context):
        frame = context['engine']['frame']

        matched = (frame is not None) and \
            self.mask_win_hook.match(frame) and \
            self.mask_lose_hook.match(frame) and \
            self.mask_win.match(frame)

        escaped = not self.matched_in(context, 1000)

        if escaped:
            self._switch_state(self._state_default)

        return matched

    def dump(self, context):
        print('--------')
        print('won: ', context['game']['won'])

        for e in context['game']['players']:
            kill = e.get('kill')
            death = e.get('death')
            score = e.get('score')
            myself = '*' if e.get('myself') else None
            print(kill, death, score, myself)

    def _init_scene(self, debug=False):
        self.mask_win_hook = IkaMatcher(
            920, 0, 100, 70,
            img_file='v2_result_scoreboard.png',
            threshold=0.90,
            orig_threshold=0.10,
            bg_method=matcher.MM_DARK(visibility=(0, 16)),
            fg_method=matcher.MM_NOT_DARK(visibility=(16, 255)),
            label='result_scoreboard:WIN',
            debug=debug,
        )

        self.mask_win = IkaMatcher(
            710, 57, 144, 66,
            img_file='v2_result_scoreboard.png',
            threshold=0.90,
            orig_threshold=0.10,
            bg_method=matcher.MM_DARK(visibility=(0, 16)),
            fg_method=matcher.MM_NOT_DARK(visibility=(16, 255)),
            label='result_scoreboard:WIN_STR',
            debug=debug,
        )

        self.mask_lose_hook = IkaMatcher(
            920, 340, 100, 70,
            img_file='v2_result_scoreboard.png',
            threshold=0.90,
            orig_threshold=0.10,
            bg_method=matcher.MM_DARK(visibility=(0, 16)),
            fg_method=matcher.MM_NOT_DARK(visibility=(16, 255)),
            label='result_scoreboard:LOSE',
            debug=debug,
        )
        self.number_recoginizer = Number2Classifier()

if __name__ == "__main__":
    ResultScoreboard.main_func()
