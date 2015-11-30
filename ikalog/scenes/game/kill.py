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

from ikalog.scenes.scene import Scene
from ikalog.utils import *
from ikalog.utils.character_recoginizer import *


class GameKill(Scene):

    def reset(self):
        super(GameKill, self).reset()

        self.last_kills = 0
        self.total_kills = 0
        self._msec_last_kill = 0
        self._msec_last_decrease = 0

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

            for i in range(delta):
                self._call_plugins('on_game_killed')

            self._msec_last_kill = context['engine']['msec']
            self._msec_last_decrease = context['engine']['msec']
            self.last_kills = kills

    def match_no_cache(self, context):
        if self.last_kills == 0 and (not self.is_another_scene_matched(context, 'GameTimerIcon')):
            return False

        frame = context['engine']['frame']

        if frame is None:
            return False

        current_kills = self.countKills(context)
        self.increment_kills(context, current_kills)

        # print('KILLS %d LAST_KILLS %d TOTAL %d' % (current_kills, self.last_kills, self.total_kills, ))
        if current_kills >= self.last_kills:
            self._msec_last_decrease = context['engine']['msec']

        # 150ms のチャタリングは無視
        if not self.matched_in(context, 150, attr='_msec_last_decrease'):
            self.last_kills = min(self.last_kills, current_kills)
 

        return self.last_kills > 0

    def dump(self, context):
        pass

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
