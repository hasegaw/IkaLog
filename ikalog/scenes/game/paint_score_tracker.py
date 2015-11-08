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

from ikalog.scenes.scene import Scene
from ikalog.utils import *


class PaintScoreTracker(Scene):

    def match_no_cache(self, context):
        if self.is_another_scene_matched(context, 'GameTimerIcon') == False:
            return False

        frame = context['engine']['frame']

        if frame is None:
            return False

        x_list = [938, 988, 1032, 1079]

        paint_score = 0
        for x in x_list:
            # Extract a digit.
            img = context['engine']['frame'][33:33 + 41, x:x + 37, :]

            # Check if the colr distribution in in expected range.
            img_gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
            hist = cv2.calcHist([img_gray], [0], None, [5], [0, 256])
            try:
                black_raito = hist[0] / np.sum(hist)
                black_white_raito = (hist[0] + hist[4]) / np.sum(hist)
            except ZeroDivisionError:
                score = 0

            if (black_raito < 0.5) or (0.8 < black_raito) or \
                    (black_white_raito < 0.8):
                # Seems not to be a white character on black background.
                return None

            # Recoginize a digit.
            digit = self.number_recoginizer.match_digits(
                img,
                num_digits=(1, 1),
                char_width=(11, 40),
                char_height=(28, 33),
            )

            if digit is None:
                return None

            paint_score = (paint_score * 10) + digit

        # Set latest paint_score to the context.
        last_paint_score = context['game'].get('paint_score', 0)
        if last_paint_score != paint_score:
            context['game']['paint_score'] = \
                max(last_paint_score, paint_score)
            self._call_plugins('on_game_paint_score_update')
        return True

    def _analyze(self, context):
        pass

    def dump(self, context):
        print('paint_score %s' % context['game'].get('paint_score', None))

    def _init_scene(self, debug=False):
        try:
            self.number_recoginizer = character_recoginizer.NumberRecoginizer()
        except:
            self.number_recoginizer = None

if __name__ == "__main__":
    PaintScoreTracker.main_func()
