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

import time

import cv2
import numpy as np

from ikalog.api import APIClient
from ikalog.scenes.stateful_scene import StatefulScene
from ikalog.utils import *


class Downie(StatefulScene):

    def reset(self):
        super(Downie, self).reset()
        self._last_lottery_start_msec = - 100 * 1000

    def _analyze(self, context):
        pass

    # Brand

    def _extract_brand_image(self, frame):
        return frame[228:228 + 44, 954:954 + 44, :]

    def _detect_gear_brand(self, gear_brand_image):
        # FIXME
        try:
            gear_brands_knn = GearBrandRecoginizer()
            gear_brands_knn.load_model_from_file()
            gear_brands_knn.knn_train()
            result, distance = gear_brands_knn.match(gear_brand_image)
            return result
        except:
            return None

    # Gear Model

    def _extract_gear_image(self, frame):
        return frame[289:289 + 110, 547:547 + 120, :]

    # Gear Level

    def _extract_gear_level_image(self, frame):
        return frame[408:408 + 18, 579:579 + 60, :]

    def _detect_gear_level(self, gear_level_image):
        img_level = matcher.MM_COLOR_BY_HUE(
            hue=(30 - 5, 30 + 5), visibility=(200, 255)).evaluate(gear_level_image)
        cv2.imshow('level', img_level)
        img_level_hist = np.sum(img_level / 255, axis=0)
        img_level_x = np.extract(img_level_hist > 3, np.arange(1024))

        level_width = np.amax(img_level_x) - np.amin(img_level_x)

        if level_width < 10:
            return 1

        elif level_width < 40:
            return 2

        return 3

    # Sub abilities

    def _extract_sub_images(self, frame):
        img_subs = []
        for x in (718, 791, 864):
            img_sub = np.array(frame[389: 389 + 53, x:x + 55, :])
            img_sub = cv2.resize(img_sub, (52, 50))
            img_subs.append(img_sub)
        return img_subs

    def _detect_gear_abilities(self, img_subs):
        # FIXME: Exception handling
        return self._client_local.recoginize_abilities(img_subs)

    ##
    # Detect constant gear parameters from the screenshot.
    # Constant parameters: img_brand, img_gear, level
    #
    def _detect_gear_info(self, context):
        img_brand = self._extract_brand_image(context['engine']['frame'])
        img_gear = self._extract_gear_image(context['engine']['frame'])
        img_level = self._extract_gear_level_image(context['engine']['frame'])
        img_subs = self._extract_sub_images(context['engine']['frame'])

        brand = self._detect_gear_brand(img_brand)
        level = self._detect_gear_level(img_level)

        context['game']['downie'] = {
            'img_brand': img_brand,
            'img_gear': img_gear,
            'img_level': img_level,
            'img_subs': img_subs,

            'level': level,
            'brand': brand,
        }

    ##
    # Detect lottery results from the screenshots.
    # 3X Sub abilitiees
    #
    def _detect_gear_lottery_result(self, context):
        img_subs = context['game'].get('downie', {}).get('img_subs', None)
        if img_subs is None:
            return False

        sub_abilities = self._detect_gear_abilities(img_subs)
        context['game']['downie']['sub_abilities'] = sub_abilities
        return True

    def _detect_sazae_and_cash(self, frame):
        img_num_sazae = frame[137:137 + 30, 936:936 + 75]
        img_cash = frame[137:137 + 30, 1054:1052 + 175]

        cash = None
        sazae = None
        if 1:  # try:
            cash = self.number_recoginizer.match_digits(
                img_cash,
                num_digits=(7, 7),
                char_width=(5, 20),
                char_height=(16, 24),
            )

        if 1:
            sazae = self.number_recoginizer.match_digits(
                img_num_sazae,
                num_digits=(3, 3),
                char_width=(5, 20),
                char_height=(16, 24),
            )
        return {'cash': cash, 'sazae': sazae}

    def _state_default(self, context):
        if self.is_another_scene_matched(context, 'GameTimerIcon'):
            return False

        frame = context['engine'].get('frame', None)
        if frame is None:
            return False

        if not self.mask_cancel.match(frame):
            return False

        if not self.mask_gear_window.match(frame):
            return False

        if not self.mask_run.match(frame):
            r = self._detect_sazae_and_cash(frame)
            context['game']['downie'] = {
                'cash': r['cash'],
                'sazae': r['sazae'],
            }
            return False

        if self.matched_in(context, 5000, attr='_last_lottery_start_msec'):
            return False

        if not 'downie' in context:
            context['game']['downie'] = {}

        context['game']['downie'] = {
            'sazae_pre': context['game']['downie'].get('sazae', None),
            'cash_pre': context['game']['downie'].get('cash', None),
        }

        self._last_lottery_stat_msec = context['engine']['msec']
        self._last_sub_images = None
        self._last_sub_images_msec = None

        self._switch_state(self._state_lottery_running)
        return True

    # Scene entrypoints

    def _state_lottery_running(self, context):
        if self.is_another_scene_matched(context, 'GameTimerIcon'):
            return False

        frame = context['engine'].get('frame', None)
        if frame is None:
            return False

        if not self.mask_gear_window.match(frame):
            # FIXME
            # not self.matched_in(context, 15000,
            # attr='_last_lottery_start_msec'):
            if 0:
                # We're lost.
                IkaUtils.dprint('%s: Unexpected scene transition.' % self)
                self._switch_state(self._state_default)
                return False

            else:
                return True

        img_subs = []

        for x in (703, 783, 863):
            img_sub = np.array(
                frame[378: 378 + 70, x:x + 70, :], dtype=np.int16)
            img_subs.append(img_sub)

        if self._last_sub_images_msec is None:
            self._last_sub_images = img_subs
            self._last_sub_images_msec = context['engine']['msec']
            return True

        # compare the image with last image
        diff_max_list = []
        for i in range(len(img_subs)):
            img_sub_diff = abs(img_subs[i] - self._last_sub_images[i])
            diff_max_list.append(np.amax(img_sub_diff))

        diff_max = np.amax(diff_max_list)

        if (diff_max < 20) and ((context['engine']['msec'] - self._last_sub_images_msec) > 2500):
            if 0:
                cv2.imwrite('gacha_done.png', context['engine']['frame'])

            self._detect_gear_info(context)
            self._detect_gear_lottery_result(context)
            r = self._detect_sazae_and_cash(frame)
            context['game']['downie']['sazae'] = r['sazae']
            context['game']['downie']['cash'] = r['cash']
            self._call_plugins('on_inkopolis_lottery_done')

            self._switch_state(self._state_default)
            return True

        if (diff_max > 20):
            self._last_sub_images_msec = context['engine']['msec']

        self._last_sub_images = img_subs
        return True

    def dump(self, context):
        self._detect_gear_info(context)
        self._detect_gear_lottery_result(context)

        for key in context['game']['downie'].keys():
            if key.startswith('img_'):
                print('  %s: (image)' % (key))
            else:
                print('  %s: %s' % (key, context['game']['downie'][key]))
        cv2.imshow('img_brand', context['game']['downie']['img_brand'])
        cv2.imshow('img_gear', context['game']['downie']['img_gear'])

        cv2.imwrite('training/brand_%s.png' % time.time(),
                    context['game']['downie']['img_brand'])
        cv2.imwrite('training/gear_%s.png' % time.time(),
                    context['game']['downie']['img_gear'])
        cv2.waitKey(1000)

    # For debug and development
    def on_key_press(self, context, key):
        if (key != ord('d')) and (key != ord('d')):
            return False
#        if self.match(context) != True:
#            return False

        self.dump(context)

    def _init_scene(self, debug=False):
        self.mask_gear_window = IkaMatcher(
            430, 165, 640, 90,
            img_file='downie_lottery.png',
            threshold=0.9,
            orig_threshold=0.100,
            bg_method=matcher.MM_NOT_BLACK(),
            fg_method=matcher.MM_BLACK(),
            label='downie/slot_window',
            debug=debug,
        )

        self.mask_cancel = IkaMatcher(
            562, 569, 73, 20,
            img_file='downie_lottery.png',
            threshold=0.9,
            orig_threshold=0.100,
            bg_method=matcher.MM_NOT_WHITE(),
            fg_method=matcher.MM_WHITE(),
            label='downy/cancel',
            debug=debug,
        )

        self.mask_run = IkaMatcher(
            814, 569, 123, 42,
            img_file='downie_lottery.png',
            threshold=0.9,
            orig_threshold=0.100,
            bg_method=matcher.MM_NOT_WHITE(),
            fg_method=matcher.MM_WHITE(),
            label='downy/run',
            debug=debug,
        )

        self.number_recoginizer = NumberRecoginizer()
        self._client_local = APIClient(local_mode=True)

if __name__ == "__main__":
    Downie.main_func()
