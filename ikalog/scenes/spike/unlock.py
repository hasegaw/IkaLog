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
from ikalog.scenes.spike.spike import *


class SpikeUnlock(StatefulScene):

    def detect_gear_unlock_result(self, context):
        img_subs = context['game'].get('downie', {}).get('img_subs', None)
        if img_subs is None:
            return False

        sub_abilities = detect_gear_abilities(img_subs)
        context['game']['downie']['sub_abilities'] = sub_abilities
        return True

    def reset(self):
        super(SpikeUnlock, self).reset()
        self._last_unlock_start_msec = - 100 * 1000

    def _analyze(self, context):
        pass

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
            context['game']['downie'] = {}
            context['game']['downie']['cash'] = detect_cash(frame)
            context['game']['downie']['snails'] = detect_snails(frame)
            return False

        if self.matched_in(context, 5000, attr='_last_unlock_start_msec'):
            return False

        if not 'downie' in context:
            context['game']['downie'] = {}

        context['game']['downie'] = {
            'snails_pre': context['game']['downie'].get('snails', None),
            'cash_pre': context['game']['downie'].get('cash', None),
        }

        self._last_unlock_start_msec = context['engine']['msec']
        self._last_sub_images = None
        self._last_sub_images_msec = None

        self._switch_state(self._state_running)
        return True

    # Scene entrypoints

    def _state_running(self, context):
        cv2.waitKey(100)
        if self.is_another_scene_matched(context, 'GameTimerIcon'):
            return False

        frame = context['engine'].get('frame', None)
        if frame is None:
            return False

        cv2.imshow('a', context['engine']['frame'])
        if not self.mask_gear_window.match(frame):
            # FIXME
            # not self.matched_in(context, 15000,
            # attr='_last_unlock_start_msec'):
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

            detect_gear_info(context)
            self.detect_gear_unlock_result(context)
            context['game']['downie']['cash'] = detect_cash(frame)
            context['game']['downie']['snails'] = detect_snails(frame)
            self._call_plugins('on_spike_unlock_done')

            self._switch_state(self._state_default)
            return True

        if (diff_max > 20):
            self._last_sub_images_msec = context['engine']['msec']

        self._last_sub_images = img_subs
        return True

    def dump(self, context):
        detect_gear_info(context)
        self.detect_gear_unlock_result(context)

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
            img_file='spike_gear_unlock.png',
            threshold=0.9,
            orig_threshold=0.100,
            bg_method=matcher.MM_NOT_WHITE(),
            fg_method=matcher.MM_WHITE(),
            label='downy/run',
            debug=debug,
        )

if __name__ == "__main__":
    SpikeUnlock.main_func()
