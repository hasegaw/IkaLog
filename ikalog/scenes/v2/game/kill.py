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
import uuid

import cv2

from ikalog.ml.classifier import ImageClassifier

from ikalog.scenes.scene import Scene
from ikalog.utils import *
from ikalog.utils.character_recoginizer import *

from ikalog.utils.player_name import normalize_player_name


class Spl2GameKill(Scene):

    def reset(self):
        super(Spl2GameKill, self).reset()

        self.last_kills = 0
        self.total_kills = 0
        self._msec_last_kill = 0
        self._msec_last_decrease = 0

    def find_kill_messages(self, context):
        _y = 665
        killed_y = [_y, _y - 45, _y - 90, _y - 135]  # たぶん...。

        found = []
        for n in range(len(killed_y)):
            y = killed_y[n]

            # Detect kill
            img_killed = context['engine']['frame'][y: y + 25, 499:499 + 49]
            matched = self.classifier_killed.predict1(img_killed) >= 0

            if matched:
                found.append({'found': 'found'})

        return found
        while False:
            self._call_plugins(
                'on_mark_rect_in_preview',
                [(502, y), (778, y + 30)]
            )

            # crop the name part.
            img_name = img_killed[:, 25:, :]

            img_name_w = matcher.MM_WHITE(
                sat=(0, 64), visibility=(128, 255))(img_name)

            img_name_x_hist = np.extract(
                np.sum(img_name_w, axis=0) > 128,
                np.arange(img_name_w.shape[1]),
            )

            img_name_left = np.min(img_name_x_hist)
            img_name_right = np.max(img_name_x_hist - 100)

            if img_name_left >= img_name_right:
                # Cropping error?
                continue

            img_name_norm = normalize_player_name(
                img_name[:, img_name_left:img_name_right]
            )

            found.append({
                'img_kill_hid': img_name_norm,
                'pos': n,
            })

            if 0:
                cv2.imshow('img_kill_hid', img_name_w_normalized)

        return found

    def increment_kills(self, context, kills):
        num_current_kills = len(kills)
        if self.last_kills < num_current_kills:
            delta = num_current_kills - self.last_kills
            context['game']['kills'] = context['game'].get('kills', 0) + delta
            self.total_kills = context['game']['kills']

            if not ('kill_list' in context['game']):
                context['game']['kill_list'] = []

            for i in range(delta):
                kill = kills[i]
                kill['uuid'] = uuid.uuid1()
                context['game']['kill_list'].append(kill)
                self._call_plugins('on_game_killed', params=kill)

            self._msec_last_kill = context['engine']['msec']
            self._msec_last_decrease = context['engine']['msec']
            self.last_kills = num_current_kills

    def match_no_cache(self, context):
        # pass matching in some scenes.
        session = self.find_scene_object('Spl2GameSession')
        if session is not None:
            if not (session._state.__name__ in ('_state_battle')):
                return False

        frame = context['engine']['frame']

        if frame is None:
            return False

        current_kills = self.find_kill_messages(context)
        self.increment_kills(context, current_kills)

        # print('KILLS %d LAST_KILLS %d TOTAL %d' % (current_kills, self.last_kills, self.total_kills, ))
        if len(current_kills) >= self.last_kills:
            self._msec_last_decrease = context['engine']['msec']

        # 150ms のチャタリングは無視
        if not self.matched_in(context, 150, attr='_msec_last_decrease'):
            self.last_kills = min(self.last_kills, len(current_kills))

        return self.last_kills > 0

    def dump(self, context):
        pass

    def _analyze(self, context):
        pass

    def _init_scene(self, debug=False):
        self.classifier_killed = ImageClassifier(object)
        self.classifier_killed.load_from_file('data/spl2/spl2.game_kill.dat')


if __name__ == "__main__":
    Spl2GameKill.main_func()
