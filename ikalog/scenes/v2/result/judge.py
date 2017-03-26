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

import copy
import cv2
import numpy as np

from ikalog.scenes.stateful_scene import StatefulScene
from ikalog.utils import *


class V2ResultJudge(StatefulScene):

    def reset(self):
        super(V2ResultJudge, self).reset()

        self._last_img_bar_b_i16 = None
        self._last_event_msec = - 100 * 1000

    def _state_default(self, context):
        frame = context['engine']['frame']

        if frame is None:
            return False

        result = self.match_win_or_lose(context)
        if result is None:
            return False

        context['game']['judge'] = result

        self._switch_state(self._state_tracking)
        return True

    def _state_tracking(self, context):
        frame = context['engine']['frame']

        if frame is None:
            return False

        matched = self.match_win_or_lose(context) is not None

        # Exit the scene if it doesn't matched for 1000ms
        if (not matched) and (not self.matched_in(context, 1000)):
            self._switch_state(self._state_default)

        if self.matched_in(context, 30 * 1000, attr='_last_event_msec'):
            return matched

        triggered = self.match_still(context)
        if triggered:
            context['game']['image_judge'] = \
                copy.deepcopy(context['engine']['frame'])
            #self._analyze(context)
            self._call_plugins('on_result_judge')
            self._last_event_msec = context['engine']['msec']

        return matched
    
    def match_win_or_lose(self, context):
        frame = context['engine']['frame']

        r_win = self.mask_win.match(frame)
        r_lose = self.mask_lose.match(frame)

        match_win_or_lose = bool(r_win) ^ bool(r_lose)

        if not match_win_or_lose:
            return None
        return 'win' if r_win else 'lose'

    def match_still(self, context):

        img_bar = context['engine']['frame'][573:573+125, :, :]
        img_bar_b = image_filters.MM_WHITE()(img_bar)
        img_bar_b_i16 = np.array(img_bar_b, dtype=np.int16)

        if self._last_img_bar_b_i16 is None:
            self._last_img_bar_b_i16 = img_bar_b_i16
            return False

        img_diff = abs(img_bar_b_i16 - self._last_img_bar_b_i16)
        self._last_img_bar_b_i16 = img_bar_b_i16

        loss = np.sum(img_diff) / 255
        threshold = img_diff.shape[0] * img_diff.shape[1] * 0.001

        return loss < threshold

    def match1(self, context):
        frame = context['engine']['frame']

        if frame is None:
            return False

        result = self.match_win_or_lose(context)
        if result is None:
            return False

        context['game']['judge'] = result

        return True


    def _analyze(self, context):
        # Not implemented for Splatoon 2 yet

        win_ko = bool(self.mask_win_ko.match(context['engine']['frame']))
        lose_ko = bool(self.mask_lose_ko.match(context['engine']['frame']))

        # win_ko もしくは lose_ko が検出されたらノックアウト。
        # ただし以前のフレームで検出したノックアウトが検出できなくなっている
        # 場合があるので、すでにノックアウト状態であればノックアウトのまま。
        knockout = win_ko or lose_ko or context['game'].get('knockout', False)

        context['game']['knockout'] = knockout

        if knockout:
            return True

        # パーセンテージの読み取りは未実装
        return True

        # ToDo: 最新コードをマージ

    def dump(self, context):
        print('%s: matched %s analyzed %s' %
              (self.__class__.__name__, self._matched, self._analyzed))
        print('    Judge: %s' % context['game'].get('judge', None))
        print('    Knockout: %s' % context['game'].get('knockout', None))

    def _init_scene(self, debug=False):
        self.mask_win = IkaMatcher(
            0, 0, 190, 110,
            img_file='v2_result_judge_win.png',
            threshold=0.9,
            orig_threshold=0.100,
            bg_method=matcher.MM_BLACK(),
            fg_method=matcher.MM_WHITE(),
            label='result_judge/win',
            call_plugins=self._call_plugins,
            debug=debug,
        )

        self.mask_win_ko = IkaMatcher(
            123, 572, 318, 57,
            img_file='result_judge_win.png',
            threshold=0.9,
            orig_threshold=0.100,
            bg_method=matcher.MM_NOT_WHITE(),
            fg_method=matcher.MM_WHITE(),
            label='result_judge/win_ko',
            call_plugins=self._call_plugins,
            debug=debug,
        )

        self.mask_lose = IkaMatcher(
            18, 42, 126, 50,
            img_file='v2_result_judge_lose.png',
            threshold=0.9,
            orig_threshold=0.100,
            bg_method=matcher.MM_NOT_WHITE(),
            fg_method=matcher.MM_WHITE(),
            label='result_judge/lose',
            call_plugins=self._call_plugins,
            debug=debug,
        )

        self.mask_lose_ko = IkaMatcher(
            820, 572, 318, 57,
            img_file='result_judge_lose.png',
            threshold=0.9,
            orig_threshold=0.100,
            bg_method=matcher.MM_NOT_WHITE(),
            fg_method=matcher.MM_WHITE(),
            label='result_judge/lose_ko',
            call_plugins=self._call_plugins,
            debug=debug,
        )

        try:
            self.number_recoginizer = character_recoginizer.NumberRecoginizer()
        except:
            self.number_recoginizer = None

if __name__ == "__main__":
    V2ResultJudge.main_func()
