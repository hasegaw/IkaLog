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

import re

import cv2
import numpy as np

from ikalog.scenes.stateful_scene import StatefulScene
from ikalog.utils import *


class ResultFesta(StatefulScene):

    def reset(self):
        super(ResultFesta, self).reset()

        self._last_event_msec = - 100 * 1000
        self._last_analyze_msec = - 100 * 1000

    def _state_default(self, context):
        if self.is_another_scene_matched(context, 'GameTimerIcon'):
            return False

        scene_result_detail = self.find_scene_object('ResultDetail')
        if scene_result_detail is not None:
            # ResultDetail 直後 10 秒間のみ検査
            if not scene_result_detail.matched_in(context, 10 * 1000):
                return False

        frame = context['engine']['frame']

        if frame is None:
            return False

        frame = context['engine']['frame']
        matched = self.mask_fespoint_msg.match(
            frame) and self._analyze(context)

        if matched and self._analyze(context):
            # いちばん最初に取り込んだ値は初期値として採用する
            game = context['game']
            game['result_festa_exp_pre'] = game['result_festa_exp']

            self._switch_state(self._state_tracking)

        return matched

    def _state_tracking(self, context):
        frame = context['engine']['frame']

        if frame is None:
            return False

        matched = self.mask_fespoint_msg.match(
            frame) and self._analyze(context)

        # 画面が続いているならそのまま
        if matched:
            return True

        # 1000ms 以内の非マッチはチャタリングとみなす
        if not matched and self.matched_in(context, 1000):
            return False

        # それ以上マッチングしなかった場合 -> シーンを抜けている
        if not self.matched_in(context, 30 * 1000, attr='_last_event_msec'):
            self.dump(context)
            self._call_plugins('on_result_festa')

        self._last_event_msec = context['engine']['msec']
        self._switch_state(self._state_default)

        return False

    def _analyze(self, context):

        frame = context['engine']['frame']

        # 新しい称号ゲット？
        title_changed = self.mask_newtitle_msg.match(frame)

        # 数字の読み取り
        img_score = frame[435:435 + 45, 769:769 + 172]
        str_festa_exp = self.number_recoginizer.match(img_score)

        try:
            m = re.match(r"(\d+)/(\d+)", str_festa_exp)
            if m is None:
                return False

            festa_exp = int(m.group(1))
            festa_exp_max = int(m.group(2))
        except:
            # 入力値がおかしいので誤認識
            return False

        # ありえない値なら誤認識
        if (festa_exp < 0 or festa_exp > 99):
            return False

        if (festa_exp_max < 0) or (festa_exp_max > 99):
            return False

        if (festa_exp_max < festa_exp):
            return False

        game = context['game']
        game['result_festa_exp'] = festa_exp
        game['result_festa_title_changed'] = title_changed
        return True

    def dump(self, context):
        game = context['game']
        print(
            '%s:  festa change: %s -> %s title_changed %s' % (
                self,
                game.get('result_festa_exp_pre', None),
                game.get('result_festa_exp', None),
                game.get('result_festa_title_changed', None),
            ))

    def _init_scene(self, debug=False):
        self.mask_fespoint_msg = IkaMatcher(
            509, 253, 231, 38,
            img_file='masks/result_festa.png',
            threshold=0.90,
            orig_threshold=0.200,
            fg_method=matcher.MM_NOT_BLACK(),
            bg_method=matcher.MM_BLACK(),
            label='result_splatfesta/fes_point',
            debug=debug,
        )

        self.mask_newtitle_msg = IkaMatcher(
            339, 316, 249, 31,
            img_file='masks/result_festa.png',
            threshold=0.90,
            orig_threshold=0.500,  # 0.350 ぐらい
            fg_method=matcher.MM_COLOR_BY_HUE(
                hue=(31 - 5, 31 + 5), visibility=(230, 255)),
            bg_method=matcher.MM_BLACK(),
            label='result_splatfesta/fes_newtitle',
            debug=debug,
        )

        self.number_recoginizer = character_recoginizer.NumberRecoginizer()

if __name__ == "__main__":
    ResultFesta.main_func()
    cv2.waitKey(1000)
