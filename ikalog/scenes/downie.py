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

import copy
import time

import cv2
import numpy as np

from ikalog.api import APIClient
from ikalog.scenes.stateful_scene import StatefulScene
from ikalog.utils import *


class Downie(StatefulScene):

    def reset(self):
        super(Downie, self).reset()
        self._last_slot_start_msec = - 100 * 1000

    def _detect_gear_ability(self, context):
        img_subs = []
        for x in (718, 792, 864):
            img_sub = np.array(context['engine']['frame'][
                               389: 389 + 53, x:x + 55, :])
            img_subs.append(img_sub)

        context['game']['downie'] = {'sub_abilities': []}
        abilitiy_images = []
        # FIXME: run in another thread, since API client may take several
        # seconds
        for img_sub in img_subs:
            img_sub = cv2.resize(img_sub, (52, 50))
            cv2.imwrite('gacha_%s.png' % time.time(), img_sub)
            abilitiy_images.append(img_sub)

        # FIXME: Exception handling
        context['game']['downie']['sub_abilities'] = \
            self._client_local.recoginize_abilities(abilitiy_images)
        self._call_plugins('on_inkopolis_slot_done')

    def _state_default(self, context):
        frame = context['engine']['frame']

        if not self.mask0.match(frame):
            return False

        if not self.mask1.match(frame):
            return False

        if not self.mask1.match(frame):
            return False

        if self.matched_in(context, 5000, attr='_last_slot_start_msec'):
            return False

        self._last_slot_stat_msec = context['engine']['msec']
        self._last_sub_images = None
        self._last_sub_images_msec = None

        self._switch_state(self._state_slot_running)

    def _state_slot_running(self, context):
        img_sub1 = np.array(context['engine']['frame'][
                            378: 378 + 70, 703:703 + 70, :], dtype=np.int16)
        img_sub2 = np.array(context['engine']['frame'][
                            378: 378 + 70, 783:783 + 70, :], dtype=np.int16)
        img_sub3 = np.array(context['engine']['frame'][
                            378: 378 + 70, 863:863 + 70, :], dtype=np.int16)
        img_subs = [img_sub1, img_sub2, img_sub3]

        if self._last_sub_images_msec is None:
            self._last_sub_images = img_subs
            self._last_sub_images_msec = context['engine']['msec']
            return True

        # compare the image with last image
        diff_max_list = []
        for i in range(len(img_subs)):
            img_sub_diff = abs(img_subs[i] - self._last_sub_images[i])
#            cv2.imshow(str(i), np.array(img_sub_diff, dtype=np.uint8))
            diff_max_list.append(np.amax(img_sub_diff))

        diff_max = np.amax(diff_max_list)

        if (diff_max < 20) and ((context['engine']['msec'] - self._last_sub_images_msec) > 2500):
            cv2.imwrite('gacha_done.png', context['engine']['frame'])
            self._detect_gear_ability(context)

            self._last_slot_stat_msec = context['engine']['msec']
            self._switch_state(self._state_default)

        if (diff_max > 20):
            self._last_sub_images_msec = context['engine']['msec']

        self._last_sub_images = img_subs

    def dump(self, context):
        pass

    def _init_scene(self, debug=False):
        self.mask_win = IkaMatcher(
            430, 165, 640, 90,
            img_file='downy2.png',
            threshold=0.9,
            orig_threshold=0.100,
            bg_method=matcher.MM_NOT_BLACK(),
            fg_method=matcher.MM_BLACK(),
            label='downy/2',
            debug=debug,
        )

        self.mask0 = IkaMatcher(
            562, 569, 73, 20,
            img_file='downy.png',
            threshold=0.9,
            orig_threshold=0.100,
            bg_method=matcher.MM_NOT_WHITE(),
            fg_method=matcher.MM_WHITE(),
            label='downy/go',
            debug=debug,
        )

        self.mask1 = IkaMatcher(
            814, 569, 123, 42,
            img_file='downy.png',
            threshold=0.9,
            orig_threshold=0.100,
            bg_method=matcher.MM_NOT_WHITE(),
            fg_method=matcher.MM_WHITE(),
            label='downy/go',
            debug=debug,
        )

        self._client_local = APIClient(local_mode=True)

if __name__ == "__main__":
    Downie.main_func()
