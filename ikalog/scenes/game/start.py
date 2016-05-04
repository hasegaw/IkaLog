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

from ikalog.scenes.stateful_scene import StatefulScene
from ikalog.utils import *
from ikalog.constants import stages, rules


class GameStart(StatefulScene):

    # 720p サイズでの値
    mapname_width = 430
    mapname_left = 1280 - mapname_width
    mapname_top = 580
    mapname_height = 640 - mapname_top

    rulename_left = 640 - 120
    rulename_right = 640 + 120
    rulename_width = rulename_right - rulename_left
    rulename_top = 250
    rulename_bottom = 310
    rulename_height = rulename_bottom - rulename_top

    def reset(self):
        super(GameStart, self).reset()
        self.stage_votes = []
        self.rule_votes = []

        self._last_event_msec = - 100 * 1000
        self._last_run_msec = - 100 * 1000

    def find_best_match(self, frame, matchers_list):
        most_possible = (0, None)

        for matcher in matchers_list:
            matched, fg_score, bg_score = matcher.match_score(frame)
            if matched and (most_possible[0] < fg_score):
                most_possible = (fg_score, matcher)

        return most_possible[1]

    def elect(self, context, votes):
        # 古すぎる投票は捨てる
        election_start = context['engine']['msec'] - self.election_period

        while (len(votes) and votes[0][0] < election_start):
            del votes[0]

        # 考えづらいがゼロ票なら開票しない
        if len(votes) == 0:
            return None

        # 開票作業
        items = {}

        count = 0
        item_top = (0, None)  # 最高票数の tuple   (17[票], <IkaMatcher>)

        for vote in votes:
            if vote[1] is None:
                continue

            item = vote[1]
            items[item] = items[item] + 1 if item in items else 1
            if item_top[0] < items[item]:
                item_top = (items[item], item)

        # TODO: 必要票数

        if item_top[1] is None:
            return None

        return item_top[1]

    def _state_default(self, context):
        timer_icon = self.find_scene_object('GameTimerIcon')
        if (timer_icon is not None) and timer_icon.matched_in(context, 3000):
            return False


        frame = context['engine']['frame']

        if frame is None:
            return False

        if self.matched_in(context, 1500, attr='_last_run_msec'):
            return False
        else:
            self._last_run_msec = context['engine']['msec']

        stage = self.find_best_match(frame, self.stage_matchers)
        rule = self.find_best_match(frame, self.rule_matchers)

        if not stage is None:
            context['game']['map'] = stage

        if not rule is None:
            context['game']['rule'] = rule

        if stage or rule:
            self.stage_votes = []
            self.rule_votes = []
            self.stage_votes.append((context['engine']['msec'], stage))
            self.rule_votes.append((context['engine']['msec'], rule))
            self._switch_state(self._state_tracking)

        return (stage or rule)

    def _state_tracking(self, context):
        frame = context['engine']['frame']

        if frame is None:
            return False

        stage = self.find_best_match(frame, self.stage_matchers)
        rule = self.find_best_match(frame, self.rule_matchers)

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
                context['game']['start_offset_msec'] = context['engine']['msec']

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
            print('stage', v[0], v[1].id_)

        for v in self.rule_votes:
            if v[1] is None:
                continue
            print('rule', v[0], v[1].id_)

    def _init_scene(self, debug=False):
        self.election_period = 5 * 1000  # msec

        self.stage_matchers = []
        self.rule_matchers = []

        for stage_id in stages.keys():
            stage = IkaMatcher(
                self.mapname_left, self.mapname_top, self.mapname_width, self.mapname_height,
                img_file='stage_%s.png' % stage_id,
                threshold=0.95,
                orig_threshold=0.30,
                bg_method=matcher.MM_NOT_WHITE(),
                fg_method=matcher.MM_WHITE(),
                label='stage:%s' % stage_id,
                call_plugins=self._call_plugins,
                debug=debug,
            )
            self.stage_matchers.append(stage)
            setattr(stage, 'id_', stage_id)

        for rule_id in rules.keys():
            rule = IkaMatcher(
                self.rulename_left, self.rulename_top, self.rulename_width, self.rulename_height,
                img_file='rule_%s.png' % rule_id,
                threshold=0.95,
                orig_threshold=0.30,
                bg_method=matcher.MM_NOT_WHITE(),
                fg_method=matcher.MM_WHITE(),
                label='rule:%s' % rule_id,
                call_plugins=self._call_plugins,
                debug=debug,
            )
            setattr(rule, 'id_', rule_id)
            self.rule_matchers.append(rule)

if __name__ == "__main__":
    GameStart.main_func()
