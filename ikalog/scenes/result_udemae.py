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

import cv2
import numpy as np

from ikalog.scenes.stateful_scene import StatefulScene
from ikalog.constants import udemae_strings
from ikalog.utils import *


class ResultUdemae(StatefulScene):

    def reset(self):
        super(ResultUdemae, self).reset()

        self._last_event_msec = - 100 * 1000
        self._last_analyze_msec = - 100 * 1000

    def _state_default(self, context):
        if self.is_another_scene_matched(context, 'GameTimerIcon'):
            return False

        frame = context['engine']['frame']

        if frame is None:
            return False

        frame = context['engine']['frame']
        matched = self.mask_udemae_msg.match(frame) and self._analyze(context)

        if matched and self._analyze(context):
            # いちばん最初に取り込んだ値は初期値として採用する
            game = context['game']
            game['result_udemae_str_pre'] = game['result_udemae_str']
            game['result_udemae_exp_pre'] = game['result_udemae_exp']

            self._switch_state(self._state_tracking)

        return matched

    def _state_tracking(self, context):
        frame = context['engine']['frame']

        if frame is None:
            return False

        matched = self.mask_udemae_msg.match(frame) and self._analyze(context)

        # 画面が続いているならそのまま
        if matched:
            return True

        # 1000ms 以内の非マッチはチャタリングとみなす
        if not matched and self.matched_in(context, 1000):
            return False

        # それ以上マッチングしなかった場合 -> シーンを抜けている
        if not self.matched_in(context, 30 * 1000, attr='_last_event_msec'):

            # >>>>> To be removed: emulates old interface.
            game = context['game']
            context['scenes']['result_udemae'] = {}
            context['scenes']['result_udemae'][
                'udemae_str'] = game['result_udemae_str_pre']
            context['scenes']['result_udemae'][
                'udemae_exp'] = game['result_udemae_exp_pre']
            context['scenes']['result_udemae'][
                'udemae_str_after'] = game['result_udemae_str']
            context['scenes']['result_udemae'][
                'udemae_exp_after'] = game['result_udemae_exp']
            # <<<<<

            self.dump(context)
            self._call_plugins('on_result_udemae')

        self._last_event_msec = context['engine']['msec']
        self._switch_state(self._state_default)

        return False

    def _analyze(self, context):
        udemae_str = None
        udemae_exp = None

        frame = context['engine']['frame']
        img_udemae = frame[357:357 + 108, 450:450 + 190]
        img_udemae_exp = frame[310:310 + 185, 770:770 + 110]

        # ウデマエアップ／ダウンで黄色くなるのでチェックする
        filter_white = matcher.MM_WHITE()
        filter_yellow = matcher.MM_COLOR_BY_HUE(
            hue=(31 - 5, 31 + 5), visibility=(230, 255))

        img_udemae_white = filter_white.evaluate(img_udemae)
        img_udemae_yellow = filter_yellow.evaluate(img_udemae)

        # 文字色が白より黄色ならウデマエアップ(ダウン)
        score_white = np.sum(img_udemae_white)
        score_yellow = np.sum(img_udemae_yellow)
        udemae_str_changed = score_white < score_yellow

        # 文字認識が白専用なので、ウデマエ文字列が黄色であれば
        # 文字が白色の画像に置き換えて文字認識させる
        if udemae_str_changed:
            img_udemae = cv2.cvtColor(np.maximum(img_udemae_white, img_udemae_yellow),
                                      cv2.COLOR_GRAY2BGR)

        # ウデマエ(文字部分)
        if self.udemae_recoginizer:
            udemae_str = self.udemae_recoginizer.match(img_udemae)

        if not (udemae_str in udemae_strings):
            udemae_str = None

        # ウデマエ(数値部分)
        if self.number_recoginizer:
            udemae_exp = self.number_recoginizer.match_digits(
                img_udemae_exp)

        if (udemae_exp is not None):
            # ウデマエの数字は 0~99 しかありえない
            if (udemae_exp < 0) or (udemae_exp > 99):
                udemae_exp = None

        # ウデマエが正しく取得できない場合は別の画面を誤認識している
        # 可能性が高い

        if not (udemae_str and udemae_exp):
            return False

        game = context['game']
        game['result_udemae_str'] = udemae_str
        game['result_udemae_exp'] = udemae_exp

        return True

    def dump(self, context):
        game = context['game']
        print(
            '%s:  udemae change: %s %s -> %s %s' % (self,
                                                    game['result_udemae_str_pre'], game[
                                                        'result_udemae_exp_pre'],
                                                    game['result_udemae_str'], game[
                                                        'result_udemae_exp'],
                                                    ))

    def _init_scene(self, debug=False):

        self.mask_udemae_msg = IkaMatcher(
            561, 245, 144, 52,
            img_file='masks/result_udemae.png',
            threshold=0.90,
            orig_threshold=0.200,
            fg_method=matcher.MM_COLOR_BY_HUE(
                hue=(11 - 5, 11 + 5), visibility=(200, 255)),
            bg_method=matcher.MM_BLACK(visibility=(0, 64)),
            label='result_udemae/Udemae',
            debug=debug,
        )

        self.number_recoginizer = character_recoginizer.NumberRecoginizer()
        self.udemae_recoginizer = character_recoginizer.UdemaeRecoginizer()

if __name__ == "__main__":
    ResultJudge.main_func()
