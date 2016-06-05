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
import time

import cv2
import numpy as np

from ikalog.constants import special_weapons
from ikalog.scenes.stateful_scene import StatefulScene
from ikalog.utils import *
from ikalog.utils.character_recoginizer import *


##
# GameSpecialWeapon
#
# Detects if any special weapons are activated.
#
# EVENTS:
#
#     on_game_special_weapon()
#     Notifies special weapon activation in my team.
#         context['game']['special_weapon']
#             Id of special_weapon activated.
#
# HOW TO MANIPULATE THE MASKS:
#
#     This scene needs masks for each languages. To gather mask data,
#     Set "write_sample" in __init__() function to True.
#     It will write a sample image.
#
#     Filename of the samples should be:
#       masks/<IKALOG_LANG>/special_<SPECIAL_WEAPON_ID>.png
#
#     For SPECIAL_WEAPON_ID, check the array definition of
#      "special_weapon" array in ikalog/constants.py.
#
class GameSpecialWeapon(StatefulScene):

    def find_best_match(self, frame, matchers_list):
        most_possible = (0, None)

        for matcher in matchers_list:
            matched, fg_score, bg_score = matcher.match_score(frame)
            if matched and (most_possible[0] < fg_score):
                most_possible = (fg_score, matcher)

        return most_possible[1]

    # Called per Engine's reset.
    def reset(self):
        super(GameSpecialWeapon, self).reset()
        self.img_last_special = None

    def _match_phase1(self, context, img_special, img_last_special):
        #
        # Phase 1
        #
        # Crop the area special weapon message supposed to be appeared.
        # Compare with last frame, and check if it is (almost) same with
        # the last frame.
        #

        img_special_diff = abs(img_special - img_last_special)
        matched = bool(np.average(img_special_diff) < 90)
        return matched

    def _is_my_special_weapon(self, context, img_special_bgr):
        img = img_special_bgr[:, :150]

        img_s = cv2.cvtColor(img, cv2.COLOR_BGR2HSV)[:, :, 2]
        img_s[matcher.MM_WHITE()(img) > 127] = 127

        img_s_hist = cv2.calcHist(img_s[:, :], [0], None, [5], [0, 256])
        img_s_hist_black = float(np.amax(img_s_hist[0:1]))
        img_s_hist_non_black = float(np.amax(img_s_hist[3:4]))
        return img_s_hist_black < img_s_hist_non_black

    def _state_default(self, context):
        if not self.is_another_scene_matched(context, 'GameTimerIcon'):
            return False

        frame = context['engine']['frame']
        if frame is None:
            return False

        # FIXME: this code works with the first special weapon only
        img_special_bgr = frame[260:260 + 24, 1006:1006 + 210, :]
        img_special = np.array(img_special_bgr)
        img_last_special = self.img_last_special
        self.img_last_special = img_special

        if img_last_special is None:
            return False

        if not self._match_phase1(context, img_special, img_last_special):
            return False

        #
        # Phase 2
        #
        # Check inkling image on right side
        img_sp_char = cv2.cvtColor(
            img_special_bgr[:, 150:210], cv2.COLOR_BGR2GRAY)

        laplacian_threshold = 60
        img_laplacian = cv2.Laplacian(img_sp_char, cv2.CV_64F)
        img_laplacian_abs = cv2.convertScaleAbs(img_laplacian)
        c_matched = bool(np.average(img_laplacian_abs) > 20)

        if not c_matched:
            return False

        # Phase 3
        # TODO: Background color

        # Phase 4
        # Forground text
        white_filter = matcher.MM_WHITE()
        img_sp_text = white_filter(img_special_bgr[:, 0:150])

        special = self.find_best_match(img_special_bgr, self.masks)
        if self.write_samples:
            cv2.imwrite('training/_special_%s.png' %
                        time.time(), 255 - img_sp_text)

        if special is None:
            return False

        context['game']['special_weapon'] = special._id
        context['game']['special_weapon_is_mine'] = \
            self._is_my_special_weapon(context, img_special_bgr)
        self._call_plugins('on_game_special_weapon')

        self._switch_state(self._state_tracking)
        return True

    def _state_tracking(self, context):
        if not self.is_another_scene_matched(context, 'GameTimerIcon'):
            return False

        frame = context['engine']['frame']
        if frame is None:
            return False

        # FIXME
        img_special_bgr = frame[260:260 + 24, 1006:1006 + 210, :]
        img_special = np.array(img_special_bgr)
        img_last_special = self.img_last_special

        if img_last_special is None:
            return False

        special = self.find_best_match(img_special_bgr, self.masks)
        if special is not None:
            self._call_plugins(
                'on_mark_rect_in_preview',
                [(1006, 260), (1006 + 210, 260 + 24)]
            )

            if context['game']['special_weapon'] == special._id:
                return True

        if self.matched_in(context, 150):
            return False

        self._switch_state(self._state_default)
        self.img_last_special = None
        return False

    def dump(self, context):
        # Not implemented :\
        pass

    def _analyze(self, context):
        pass

    # Called only once on initialization.
    def _init_scene(self, debug=False):
        #
        # To gather mask data, enable this.
        #
        self.write_samples = False

        # Load mask files.
        self.masks = []
        for special_weapon in special_weapons.keys():
            try:
                mask = IkaMatcher(
                    0, 0, 150, 24,
                    img_file='special_%s.png' % special_weapon,
                    threshold=0.90,
                    orig_threshold=0.20,
                    bg_method=matcher.MM_NOT_WHITE(),
                    fg_method=matcher.MM_WHITE(),
                    label='special/%s' % special_weapon,
                    call_plugins=self._call_plugins,
                    debug=debug,
                )
                mask._id = special_weapon
                self.masks.append(mask)
            except:
                IkaUtils.dprint('%s: Failed to load mask for %s' %
                                (self, special_weapon))
                pass

if __name__ == "__main__":
    GameSpecialWeapon.main_func()
