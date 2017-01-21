#!/usr/bin/env python3
# -*- coding: utf-8 -*-
#
#  IkaLog
#  ======
#  Copyright (C) 2016 Takeshi HASEGAWA
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
from ikalog.utils.ikamatcher2.matcher import MultiClassIkaMatcher2 as MultiClassIkaMatcher


class V2GameSubAndSpecial(StatefulScene):

    def reset(self):
        super(V2GameSubAndSpecial, self).reset()
        self.img_last_special = None

    def _state_default(self, context):
        # TODO: Lookup another scene
        if self.is_another_scene_matched(context, 'V2GameSuperJump') == True:
            return False

        if self.match1(context):
            # Enter the scene
            # FIXME: the image should be reused.
            img_special, img_sub = self.extract_feature_images(context)

            self._img_last_special = np.array(img_special, dtype=np.int16)
            self._img_last_sub = np.array(img_sub, dtype=np.int16)
            self._switch_state(self._state_tracking)

            return True
        return False

    def _state_tracking(self, context):
        if self.is_another_scene_matched(context, 'V2GameSuperJump') == True:
            return False

        """
        Generate diff image
        """
        img_special, img_sub = self.extract_feature_images(context)
        img_special_i16 = np.array(img_special, dtype=np.int16)
        img_sub_i16 = np.array(img_sub, dtype=np.int16)

        img_diff_special_i16 = abs(self._img_last_special - img_special_i16)
        img_diff_sub_i16 = abs(self._img_last_sub - img_sub_i16)

        if 0:
            cv2.imshow(
                'img_diff_special',
                np.array(img_diff_special_i16, dtype=np.uint8)
            )
            cv2.imshow(
                'img_sub_special',
                np.array(img_diff_sub_i16, dtype=np.uint8)
            )

        """
        Calcurate loss and classify
        """
        loss_special = np.sum(img_diff_special_i16)
        loss_sub = np.sum(img_diff_sub_i16)
        matched = (loss_special < 100000) and (loss_sub < 100000)

        #print(matched, loss_special, loss_sub)

        # Exit the scene if it doesn't matched for 1000ms
        if (not matched) and (not self.matched_in(context, 1000)):
            self._switch_state(self._state_default)

        if (not matched):
            return False

        return True

    def match1(self, context):
        img_special, img_sub = self.extract_feature_images(context)

        """
        Special weapon
        """

        special = self._masks_special.match_best(img_special)
        special = special[1]._id if special[1] is not None else None
        # print(special)

        """
        Sub weapon: not implemented yet
        """
        sub = 'motsunabe'

        if 0:
            cv2.imshow('img_special', img_special)
            cv2.imshow('img_sub', img_sub)

        return (special is not None) and (sub is not None)

    def extract_feature_images(self, context):
        """
        Crop the area
        """
        frame = context['engine']['frame']
        img_special = frame[47:47 + 66, 1152:1152 + 66, :]
        img_sub = frame[23:23 + 42, 1133:1133 + 31, :]

        img_special = img_special & self._img_mask_special

        return img_special, img_sub

    def write_training_samples(self, context):
        img_special, img_sub = self.extract_feature_images(context)

        img_special = image_filters.MM_DARK()(img_special)
        img_sub = image_filters.MM_DARK()(img_sub)

        t = time.time()
        cv2.imwrite('img_special.%s.png' % t, img_special)
        cv2.imwrite('img_sub.%s.png' % t, img_sub)

    def dump(self, context):
        self.write_training_samples(context)

    def _analyze(self, context):
        pass

    # Called only once on initialization.
    def _init_scene(self, debug=False):
        """
        Load mask images
        """
        # FIXME: Needs constatnts for v2
        special_weapon_keys = ['sp1', 'sp2', 'sp3', 'sp4']

        self._masks_special = MultiClassIkaMatcher()
        for special_weapon in special_weapon_keys:
            try:
                mask = IkaMatcher(
                    1152, 47, 66, 66,
                    img_file='v2_game_special_icon_%s.png' % special_weapon,
                    threshold=0.85,
                    orig_threshold=0.10,
                    bg_method=matcher.MM_DARK(),
                    fg_method=matcher.MM_NOT_DARK(),
                    label='special/%s' % special_weapon,
                    call_plugins=self._call_plugins,
                    debug=debug,
                )
                mask._id = special_weapon
                self._masks_special.add_mask(mask)
            except:
                IkaUtils.dprint('%s: Failed to load mask for %s' %
                                (self, special_weapon))

        """
        Generate additional mask images
        """
        self._img_mask_special = np.zeros((66, 66, 3), dtype=np.uint8)
        cv2.circle(self._img_mask_special, (33, 33), 29, (255, 255, 255), -1)

if __name__ == "__main__":
    V2GameSubAndSpecial.main_func()
