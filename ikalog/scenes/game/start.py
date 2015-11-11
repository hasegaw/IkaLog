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

        self._last_event_msec = - 100 * 1000

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
        if self.is_another_scene_matched(context, 'GameTimerIcon'):
            return False

        frame = context['engine']['frame']

        if frame is None:
            return False

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
        if not self.matched_in(context, 1000, attr='_last_event_msec'):
            context['game']['map'] = self.elect(context, self.stage_votes)
            context['game']['rule'] = self.elect(context, self.rule_votes)

            self.dump(context)
            self._call_plugins('on_game_start')
            self._last_event_msec = context['engine']['msec']

        self._switch_state(self._state_default)
        return False

    def _analyze(self, context):
        pass

    def dump(self, context):
        print(self.stage_votes)
        print(self.rule_votes)

    def _init_scene(self, debug=False):
        self.election_period = 5 * 1000  # msec

        self.map_list = [
            {'name': 'タチウオパーキング', 'file': 'masks/gachi_tachiuo.png'},
            {'name': 'モズク農園',         'file': 'masks/nawabari_mozuku.png'},
            {'name': 'ネギトロ炭鉱',       'file': 'masks/gachi_negitoro.png'},
            {'name': 'アロワナモール',     'file': 'masks/nawabari_arowana.png'},
            {'name': 'デカライン高架下',   'file': 'masks/yagura_decaline.png'},
            {'name': 'Bバスパーク',        'file': 'masks/gachi_buspark.png'},
            {'name': 'ハコフグ倉庫',       'file': 'masks/gachi_hakofugu.png'},
            {'name': 'シオノメ油田',       'file': 'masks/gachi_shionome.png'},
            {'name': 'モンガラキャンプ場', 'file': 'masks/hoko_mongara.png'},
            {'name': 'ホッケふ頭',         'file': 'masks/nawabari_hokke.png'},
            {'name': 'ヒラメが丘団地',     'file': 'masks/nawabari_hirame.png'},
            {'name': 'マサバ海峡大橋',     'file': 'masks/nawabari_masaba.png'},
        ]

        self.rule_list = [
            {'name': 'ガチエリア',     'file': 'masks/gachi_tachiuo.png'},
            {'name': 'ガチヤグラ',     'file': 'masks/yagura_decaline.png'},
            {'name': 'ガチホコバトル', 'file': 'masks/hoko_mongara.png'},
            {'name': 'ナワバリバトル', 'file': 'masks/nawabari_mozuku.png'},
        ]

        self.stage_matchers = []
        self.rule_matchers = []

        for map in self.map_list:
            map['mask'] = IkaMatcher(
                self.mapname_left, self.mapname_top, self.mapname_width, self.mapname_height,
                img_file=map['file'],
                threshold=0.95,
                orig_threshold=0.30,
                bg_method=matcher.MM_NOT_WHITE(),
                fg_method=matcher.MM_WHITE(),
                label='map:%s' % map['name'],
                debug=debug,
            )
            self.stage_matchers.append(map['mask'])
            setattr(map['mask'], 'id_', map['name'])

        for rule in self.rule_list:
            rule['mask'] = IkaMatcher(
                self.rulename_left, self.rulename_top, self.rulename_width, self.rulename_height,
                img_file=rule['file'],
                threshold=0.95,
                orig_threshold=0.30,
                bg_method=matcher.MM_NOT_WHITE(),
                fg_method=matcher.MM_WHITE(),
                label='rule:%s' % rule['name'],
                debug=debug,
            )
            setattr(rule['mask'], 'id_', rule['name'])
            self.rule_matchers.append(rule['mask'])

if __name__ == "__main__":
    GameStart.main_func()
