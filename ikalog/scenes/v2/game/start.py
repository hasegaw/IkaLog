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

from ikalog.scenes.stateful_scene import StatefulScene
from ikalog.utils import *
#from ikalog.constants import stages, rules
from ikalog.utils.ikamatcher2.matcher import MultiClassIkaMatcher2 as MultiClassIkaMatcher


stages = {'ama': True, 'battera': True, 'fujitsubo': True, 'gangaze': True, 'combu': True, 'tachiuo': True}
rules = {'nawabari': True, 'area': True}


class V2GameStart(StatefulScene):

    def reset(self):
        super(V2GameStart, self).reset()
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

        stage = None
        rule = None

        best_stage = self.stage_matchers.match_best(frame)
        best_rule = self.rule_matchers.match_best(frame)

        if best_stage[1] is not None:
            stage = best_stage[1].id_
        if best_rule[1] is not None:
            rule = best_rule[1].id_

        return stage, rule

    def _state_default(self, context):
        frame = context['engine']['frame']
        if frame is None:
            return False

        if not self._mask_rule.match(frame):
            return False

        # Get the best matched stat.ink key
        stage, rule = self._detect_stage_and_rule(context)

        if stage or rule:
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

            if not context['game']['start_time']:
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

        self._mask_rule = IkaMatcher(
                600, 128, 77, 35,
                img_file='v2_rule_nawabari.png',
                bg_method=matcher.MM_NOT_WHITE(),
                fg_method=matcher.MM_WHITE(),
                threshold=0.9,
                orig_threshold=0.3,
                label='rule',
                debug=debug,
            )

        self.stage_matchers = MultiClassIkaMatcher()
        self.rule_matchers = MultiClassIkaMatcher()
        for stage_id in stages.keys():
            stage = IkaMatcher(
                1133, 655, 119, 34,
                img_file='v2_stage_%s.png' % stage_id,
                threshold=0.85,
                orig_threshold=0.15,
                bg_method=matcher.MM_NOT_WHITE(),
                fg_method=matcher.MM_WHITE(),
                label='stage:%s' % stage_id,
                call_plugins=self._call_plugins,
                debug=debug,
            )
            setattr(stage, 'id_', stage_id)
            self.stage_matchers.add_mask(stage)

        for rule_id in rules.keys():
            rule = IkaMatcher(
                531, 224, 227, 58,
                img_file='v2_rule_%s.png' % rule_id,
                threshold=0.70,
                orig_threshold=0.10,
                bg_method=matcher.MM_NOT_WHITE(),
                fg_method=matcher.MM_WHITE(),
                label='rule:%s' % rule_id,
                call_plugins=self._call_plugins,
                debug=debug,
            )
            setattr(rule, 'id_', rule_id)
            self.rule_matchers.add_mask(rule)

if __name__ == "__main__":
    V2GameStart.main_func()
