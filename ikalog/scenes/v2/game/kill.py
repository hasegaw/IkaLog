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

from ikalog.scenes.scene import Scene
from ikalog.utils import *
from ikalog.utils.character_recoginizer import *

from ikalog.utils.player_name import normalize_player_name

class V2GameKill(Scene):

    def reset(self):
        super(V2GameKill, self).reset()

        self.last_kills = 0
        self.total_kills = 0
        self._msec_last_kill = 0
        self._msec_last_decrease = 0

    def find_kill_messages(self, context):
        _y = 664
        killed_y = [_y]
        killed_y = [_y, _y - 40, _y - 80, _y - 120]  # たぶん...。

        found = []
        for n in range(len(killed_y)):
            y = killed_y[n]

            # Detect kill

            img_killed = context['engine']['frame'][y: y + 30, 525:778]
            img_killed_gray = cv2.cvtColor(img_killed[:, 0:25, :], cv2.COLOR_BGR2GRAY)
            ret, img_killed_thresh = cv2.threshold(img_killed_gray, 90, 255, cv2.THRESH_BINARY)
            cv2.imshow('a', img_killed_thresh)

            r = self.mask_killed.match(img_killed_thresh)
            if not r:
                continue
                # or
                return found

            self._call_plugins(
                'on_mark_rect_in_preview',
                [ (502, y), (778, y + 30) ]
            )

            # crop the name part.
            img_name = img_killed[:, 25:, :]

            img_name_w = matcher.MM_WHITE(sat=(0, 64), visibility=(128, 255))(img_name)

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
                img_name[:, img_name_left :img_name_right]
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
#        if self.last_kills == 0 and (not self.is_another_scene_matched(context, 'GameTimerIcon')):
#            return False

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
        self.mask_killed = IkaMatcher(
            0, 0, 25, 30,
            img_file='game_killed.png',
            threshold=0.80,
            orig_threshold=0.10,
            bg_method=matcher.MM_WHITE(sat=(0, 255), visibility=(0, 48)),
            fg_method=matcher.MM_WHITE(visibility=(192, 255)),
            label='killed',
            debug=debug,
        )

if __name__ == "__main__":
    V2GameKill.main_func()
