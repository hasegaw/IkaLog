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
import cv2
import numpy as np

from ikalog.scenes.scene import Scene
from ikalog.utils import *


class ResultJudge(Scene):

    def reset(self):
        super(ResultJudge, self).reset()

        self._last_event_msec = - 100 * 1000

    def match_no_cache(self, context):
        if self.is_another_scene_matched(context, 'GameTimerIcon'):
            return False

        frame = context['engine']['frame']

        if frame is None:
            return False

        match_win = self.mask_win.match(frame)
        match_lose = self.mask_lose.match(frame)

        match_win_or_lose = (match_win and (not match_lose) or
                             (match_lose and (not match_win)))

        if not match_win_or_lose:
            return False

        img_bar = context['engine']['frame'][600:600 + 30, 126:126 + 1028, :]
        img_bar_hsv = cv2.cvtColor(img_bar, cv2.COLOR_BGR2HSV)
        ret, img_bar_b = cv2.threshold(
            img_bar_hsv[:, :, 2], 96, 255, cv2.THRESH_BINARY)

        img_bar_b_hist = cv2.calcHist([img_bar_b], [0], None, [3], [0, 256])
        raito = img_bar_b_hist[2] / np.sum(img_bar_b_hist)
        #print('%s: win %s lose %s raito %s' % (self, match_win, match_lose, raito))

        if (raito < 0.9):
            return False

        context['game']['judge'] = 'win' if match_win else 'lose'

        if not self.matched_in(context, 30 * 1000, attr='_last_event_msec'):
            print('trigger event')
            context['game']['image_judge'] = copy.deepcopy(
                context['engine']['frame'])
            self._analyze(context)
            self._call_plugins('on_result_judge')
            self._last_event_msec = context['engine']['msec']

        return True

    def _analyze(self, context):
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
            73, 34, 181, 94,
            img_file='result_judge_win.png',
            threshold=0.9,
            orig_threshold=0.100,
            bg_method=matcher.MM_NOT_WHITE(),
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
            73, 34, 181, 94,
            img_file='result_judge_lose.png',
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
    ResultJudge.main_func()
