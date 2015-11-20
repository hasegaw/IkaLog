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


class GameKill(StatefulScene):

    def recoginize_and_vote_death_reason(self, context):
        if self.deadly_weapon_recoginizer is None:
            return False
        img_weapon = context['engine']['frame'][218:218 + 51, 452:452 + 410]
        img_weapon_gray = cv2.cvtColor(img_weapon, cv2.COLOR_BGR2GRAY)
        ret, img_weapon_b = cv2.threshold(
            img_weapon_gray, 230, 255, cv2.THRESH_BINARY)

        # (覚) 学習用に保存しておくのはこのデータ
        if 1:  # (self.time_last_write + 5000 < context['engine']['msec']):
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
        super(GameKill, self).reset()

        self.last_kills = 0
        self.total_kills = 0
        self._msec_last_kill = 0
        self.frames_since_last_kill = 0

    def countKills(self, context):
        img_gray = cv2.cvtColor(context['engine']['frame'][
                                :, 502:778], cv2.COLOR_BGR2GRAY)
        ret, img_thresh = cv2.threshold(img_gray, 90, 255, cv2.THRESH_BINARY)

        killed_y = [652, 652 - 40, 652 - 80, 652 - 120]  # たぶん...。
        killed = 0

        list = []
        for n in range(len(killed_y)):
            y = killed_y[n]
            box = img_thresh[y:y + 30, :]
            r = self.mask_killed.match(box)

            if r:
                list.append(n)
        return len(list)

    def increment_kills(self, context, kills):
        if self.last_kills < kills:
            delta = kills - self.last_kills
            context['game']['kills'] = context['game'].get('kills', 0) + delta
            self.total_kills = context['game']['kills']

            self._call_plugins('on_game_killed')

            self._msec_last_kill = context['engine']['msec']
            self.frames_since_last_kill = 0
            self.last_kills = kills

    def a_state_default(self, context):
        if not self.is_another_scene_matched(context, 'GameTimerIcon'):
            return False

        frame = context['engine']['frame']

        if frame is None:
            return False

        self.last_kills = 0
        current_kills = self.countKills(context)
        matched = current_kills > 0

        if matched:
            self.increment_kills(context, current_kills)
            self._switch_state(self._state_tracking)

        return matched

    def _state_default(self, context):
        if self.last_kills == 0 and (not self.is_another_scene_matched(context, 'GameTimerIcon')):
            return False

        frame = context['engine']['frame']

        if frame is None:
            return False

        current_kills = self.countKills(context)
        self.increment_kills(context, current_kills)

        # print('KILLS %d LAST_KILLS %d TOTAL %d' % (current_kills, self.last_kills, self.total_kills))
        if current_kills < self.last_kills:
            self.frames_since_last_kill = self.frames_since_last_kill + 1

        # 3秒以上 or 5 フレーム間は last_kill の値を維持する
        cond1 = self.matched_in(context, 3 * 1000, attr='_msec_last_kill')
        cond2 = (5 < self.frames_since_last_kill)

        if (cond1 or cond2):
            self.last_kills = min(self.last_kills, current_kills)

        if self.last_kills == 0:
            # self._switch_state(self._state_default)
            return False

        return True

    def dump(self, context):
        print('last_death_reason %s' % context['game']['death_reasons'])

    def _analyze(self, context):
        pass

    def _init_scene(self, debug=False):
        self.mask_killed = IkaMatcher(
            0, 0, 25, 30,
            img_file='masks/ui_killed.png',
            threshold=0.90,
            orig_threshold=0.10,
            bg_method=matcher.MM_WHITE(sat=(0, 255), visibility=(0, 48)),
            fg_method=matcher.MM_WHITE(visibility=(192, 255)),
            label='killed',
            debug=debug,
        )

if __name__ == "__main__":
    GameKill.main_func()
