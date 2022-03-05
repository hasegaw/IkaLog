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
from ikalog.ml.classifier import ImageClassifier
from ikalog.scenes.stateful_scene import StatefulScene
from ikalog.utils import *
from ikalog.utils.character_recoginizer import *


##
# Spl2GameSpecialWeaponActivation
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
class Spl2GameSpecialWeaponActivation(StatefulScene):

    # Called per Engine's reset.
    def reset(self):
        super(Spl2GameSpecialWeaponActivation, self).reset()
        self.img_last_special = None

    def _is_my_special_weapon(self, context, img_special_bgr):
        img = img_special_bgr[:, :150]

        img_s = cv2.cvtColor(img, cv2.COLOR_BGR2HSV)[:, :, 2]
        img_s[matcher.MM_WHITE()(img) > 127] = 127

        img_s_hist = cv2.calcHist(img_s[:, :], [0], None, [5], [0, 256])
        img_s_hist_black = float(np.amax(img_s_hist[0:1]))
        img_s_hist_non_black = float(np.amax(img_s_hist[3:4]))
        return img_s_hist_black < img_s_hist_non_black

    def _state_default(self, context):
        # pass matching in some scenes.
        session = self.find_scene_object('Spl2GameSession')
        if session is not None:
            if not (session._state.__name__ in ('_state_battle')):
                return False

        frame = context['engine']['frame']
        if frame is None:
            return False

        img_special_bgr = self._c.extract_rect(frame)
        special_weapon_id = self._c.predict1(img_special_bgr)

        if special_weapon_id == -1:
            return False

        context['game']['special_weapon'] = special_weapon_id
        mine = self._is_my_special_weapon(context, img_special_bgr)
        context['game']['special_weapon_is_mine'] = mine
        self._call_plugins('on_game_special_weapon', {
            'special_weapon': special_weapon_id,
            'is_my_special_weapon': mine
        })

        self._switch_state(self._state_tracking)
        return True

    def _state_tracking(self, context):
        # pass matching in some scenes.
        session = self.find_scene_object('Spl2GameSession')
        if session is not None:
            if not (session._state.__name__ in ('_state_battle')):
                return False

        # todo: ignore if map is active

        frame = context['engine']['frame']
        if frame is None:
            return False

        img_special_bgr = self._c.extract_rect(frame)
        special_weapon_id = self._c.predict1(img_special_bgr)

        if (special_weapon_id == -1) and (not self.matched_in(context, 1 * 1000)):
            self._switch_state(self._state_default)
            return False

        if special_weapon_id != context['game']['special_weapon']:
            # Seems next special weapon is active.
            # Force default state and the next one will be detected
            # in next frame.
            self._switch_state(self._state_default)
            return True

        return special_weapon_id != -1

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

        self._c = ImageClassifier(object)
        self._c.load_from_file(
            'data/spl2/spl2.game.special_weapon_activation.dat')


if __name__ == "__main__":
    Spl2GameSpecialWeaponActivation.main_func()
