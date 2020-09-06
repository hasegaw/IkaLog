#!/usr/bin/env python3
# -*- coding: utf-8 -*-
#
#  IkaLog
#  ======
#  Copyright (C) 2015 Takeshi HASEGAWA
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
import numpy as np
import copy

from ikalog.scenes.stateful_scene import StatefulScene
from ikalog.utils import *
#from ikalog.constants import stages, rules
from ikalog.utils.ikamatcher2.matcher import MultiClassIkaMatcher2 as MultiClassIkaMatcher

from ikalog.ml.classifier import ImageClassifier

stages = {'ama': True, 'battera': True, 'fujitsubo': True,
          'gangaze': True, 'combu': True, 'tachiuo': True}
rules = {'nawabari': True, }


class Spl2GameStart(StatefulScene):

    def reset(self):
        super(Spl2GameStart, self).reset()
        self.stage_votes = []
        self.rule_votes = []

        self._last_event_msec = - 100 * 1000
        self._last_run_msec = - 100 * 1000

    def elect(self, context, votes):
        # Discard too old data.
        election_start = context['engine']['msec'] - self.election_period
        votes = list(filter(lambda e: election_start < e[0], votes))

        # count
        items = {}
        for vote in votes:
            if vote[1] is None:
                continue
            key = vote[1]
            items[key] = items.get(key, 0) + 1

        # return the best key
        sorted_keys = sorted(
            items.keys(), key=lambda x: items[x], reverse=True)
        sorted_keys.extend([None])  # fallback

        return sorted_keys[0]

    def _detect_stage_and_rule(self, context):
        frame = context['engine']['frame']

        # mask white areas to black
        start_white = cv2.inRange(frame, (240, 240, 240), (255, 255, 255))

        img_test = copy.deepcopy(frame)
        img_test[start_white > 0] = (0, 0, 0)

        if not self._mask_start.match(img_test):
            return None, None
        
        (_, rule_match) = self._rule_masks.match_best(frame)
        if rule_match == None:
            rule = None
        else:
            rule = rule_match._label.replace('start/mode/', '')
            print("MATCHED", rule)
        stage = None

        return stage, rule

        stage = self._c_stage.predict_frame(context['engine']['frame'])
        rule = self._c_rule.predict_frame(context['engine']['frame'])

        if stage == -1:
            stage = None
        if rule == -1:
            rule = None

        return stage, rule

    def _state_default(self, context):
        # pass matching in some scenes.
        session = self.find_scene_object('Spl2GameSession')
        if session is not None:
            if not (session._state.__name__ in ('_state_default')):
                return False

        frame = context['engine']['frame']
        if frame is None:
            return False

        stage, rule = self._detect_stage_and_rule(context)

        matched = (stage or rule)

        if matched:
            self.stage_votes = []
            self.rule_votes = []
            self.stage_votes.append((context['engine']['msec'], stage))
            self.rule_votes.append((context['engine']['msec'], rule))
            self._switch_state(self._state_tracking)
            return True

        return False

    def _state_tracking(self, context):
        frame = context['engine']['frame']

        if frame is None:
            return False

        stage, rule = self._detect_stage_and_rule(context)
        matched = (stage or rule)

        # 画面が続いているならそのまま
        if matched:
            self.stage_votes.append((context['engine']['msec'], stage))
            self.rule_votes.append((context['engine']['msec'], rule))
            return True

        # 1000ms 以内の非マッチはチャタリングとみなす
        if not matched and self.matched_in(context, 1000):
            return False

        # それ以上マッチングしなかった場合 -> シーンを抜けている
        if not self.matched_in(context, 20000, attr='_last_event_msec'):
            context['game']['map'] = self.elect(context, self.stage_votes)
            context['game']['rule'] = self.elect(context, self.rule_votes)
            print(self.rule_votes)

            if not context['game']['start_time']:
                print("SETTING FALLBACK START TIME")
                # start_time should be initialized in GameGoSign.
                # This is a fallback in case GameGoSign was skipped.
                context['game']['start_time'] = IkaUtils.getTime(context)
                context['game']['start_offset_msec'] = \
                    context['engine']['msec']

            self._call_plugins('on_game_start')
            self._last_event_msec = context['engine']['msec']

        self._switch_state(self._state_default)
        return False

    def _analyze(self, context):
        pass

    def dump(self, context):
        for v in self.stage_votes:
            if v[1] is None:
                continue
            print('stage', v[0], v[1])

        for v in self.rule_votes:
            if v[1] is None:
                continue
            print('rule', v[0], v[1])

    def _init_scene(self, debug=False):
        self.election_period = 5 * 1000  # msec
        self._c_stage = ImageClassifier()
        self._c_stage.load_from_file('data/spl2/spl2.game_start.stage.dat')
        self._c_rule = ImageClassifier()
        self._c_rule.load_from_file('data/spl2/spl2.game_start.rule.dat')

        self._mask_start = IkaMatcher(
            458, 103, 369, 338,
            img_file='v2_start_mode.png',
            threshold= 0.8,
            orig_threshold= 0.1,
            bg_method=matcher.MM_DARK(visibility=(20, 255)),
            fg_method=matcher.MM_BLACK(),
            label='start/mode',
            call_plugins=self._call_plugins,
            debug=False
        )


        self._rule_masks = MultiClassIkaMatcher()
        self._rule_masks.add_mask(
            IkaMatcher(
                470, 222, 343, 131,
                img_file='v2_mode_rainmaker.png',
                threshold= 0.9,
                orig_threshold= 0.1,
                bg_method=matcher.MM_BLACK(visibility=(0, 215)),
                fg_method=matcher.MM_WHITE(visibility=(150,255)),
                label='start/mode/hoko',
                call_plugins=self._call_plugins,
                debug=False
            )
        )
        self._rule_masks.add_mask(
            IkaMatcher(
                470, 222, 343, 131,
                img_file='v2_mode_splatzone.png',
                threshold= 0.9,
                orig_threshold= 0.1,
                bg_method=matcher.MM_BLACK(visibility=(0, 215)),
                fg_method=matcher.MM_WHITE(visibility=(150,255)),
                label='start/mode/area',
                call_plugins=self._call_plugins,
                debug=False
            )
        )
        self._rule_masks.add_mask(
            IkaMatcher(
                470, 222, 343, 131,
                img_file='v2_mode_tower_control.png',
                threshold= 0.9,
                orig_threshold= 0.1,
                bg_method=matcher.MM_BLACK(visibility=(0, 215)),
                fg_method=matcher.MM_WHITE(visibility=(150,255)),
                label='start/mode/yagura',
                call_plugins=self._call_plugins,
                debug=False
            )
        )


if __name__ == "__main__":
    Spl2GameStart.main_func()
