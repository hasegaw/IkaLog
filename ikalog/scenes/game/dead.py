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
from ikalog.utils.character_recoginizer import *


class GameDead(StatefulScene):

    def recoginize_and_vote_death_reason(self, context):
        if self.deadly_weapon_recoginizer is None:
            return False
        img_weapon = context['engine']['frame'][218:218 + 51, 452:452 + 410]
        img_weapon_gray = cv2.cvtColor(img_weapon, cv2.COLOR_BGR2GRAY)
        ret, img_weapon_b = cv2.threshold(
            img_weapon_gray, 230, 255, cv2.THRESH_BINARY)

        # (覚) 学習用に保存しておくのはこのデータ
        if 0:  # (self.time_last_write + 5000 < context['engine']['msec']):
            import time
            filename = os.path.join(
                'training', '_deadly_weapons.%s.png' % time.time())
            cv2.imwrite(filename, img_weapon_b)
            self.time_last_write = context['engine']['msec']

        img_weapon_b_bgr = cv2.cvtColor(img_weapon_b, cv2.COLOR_GRAY2BGR)
        weapon_id = self.deadly_weapon_recoginizer.match(img_weapon_b_bgr)

        # 投票する(あとでまとめて開票)
        votes = self._cause_of_death_votes
        votes[weapon_id] = votes.get(weapon_id, 0) + 1

    def count_death_reason_votes(self, context):
        votes = self._cause_of_death_votes
        if len(votes) == 0:
            return None
        print('votes=%s' % votes)

        most_possible_id = None
        most_possible_count = 0
        for weapon_id in votes.keys():
            weapon_count = votes[weapon_id]
            if most_possible_count < weapon_count:
                most_possible_id = weapon_id
                most_possible_count = weapon_count

        if (most_possible_count == 0) or (most_possible_id is None):
            return None

        context['game']['last_death_reason'] = most_possible_id
        context['game']['death_reasons'][most_possible_id] = \
            context['game']['death_reasons'].get(most_possible_id, 0) + 1

        return most_possible_id

    def reset(self):
        super(GameDead, self).reset()

        self._last_event_msec = - 100 * 1000
        self._cause_of_death_votes = {}

    def _state_default(self, context):
        if not self.is_another_scene_matched(context, 'GameTimerIcon'):
            return False

        frame = context['engine']['frame']

        if frame is None:
            return False

        matched = self.mask_dead.match(context['engine']['frame'])

        if matched:
            context['game']['dead'] = True
            self._call_plugins('on_game_dead')
            self.recoginize_and_vote_death_reason(context)
            self._switch_state(self._state_tracking)

        return matched

    def _state_tracking(self, context):
        frame = context['engine']['frame']

        if frame is None:
            return False

        matched = self.mask_dead.match(context['engine']['frame'])

        # 画面が続いているならそのまま
        if matched:
            self.recoginize_and_vote_death_reason(context)
            return True

        # 1000ms 以内の非マッチはチャタリングとみなす
        if not matched and self.matched_in(context, 1000):
            return False

        # それ以上マッチングしなかった場合 -> シーンを抜けている
        if not self.matched_in(context, 5 * 1000, attr='_last_event_msec'):
            self.count_death_reason_votes(context)

            self.dump(context)
            self._call_plugins('on_game_death_reason_identified')
            self._call_plugins('on_game_respawn')

        self._last_event_msec = context['engine']['msec']
        self._switch_state(self._state_default)
        context['game']['dead'] = False
        self._cause_of_death_votes = {}

        return False

    def dump(self, context):
        print('last_death_reason %s' % context['game']['death_reasons'])

    def _analyze(self, context):
        pass

    def _init_scene(self, debug=False):
        self.mask_dead = IkaMatcher(
            1057, 657, 137, 26,
            img_file='game_dead.png',
            threshold=0.90,
            orig_threshold=0.30,
            bg_method=matcher.MM_WHITE(sat=(0, 255), visibility=(0, 48)),
            fg_method=matcher.MM_WHITE(visibility=(192, 255)),
            label='dead',
            debug=debug,
        )

        try:
            self.deadly_weapon_recoginizer = DeadlyWeaponRecoginizer()
        except:
            self.deadly_weapon_recoginizer = None

if __name__ == "__main__":
    GameDead.main_func()
