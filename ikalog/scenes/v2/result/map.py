#!/usr/bin/env python3
# -*- coding: utf-8 -*-
#
#  IkaLog
#  ======
#  Copyright (C) 2018 Takeshi HASEGAWA
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

from ikalog.ml.classifier import ImageClassifier
from ikalog.scenes.stateful_scene import StatefulScene
from ikalog.utils import *


class Spl2ResultMap(StatefulScene):

    def reset(self):
        super(Spl2ResultMap, self).reset()

        self._last_img_bar_b_i16 = None
        self._last_event_msec = - 100 * 1000

        self._smallest_max = 255
        self._highest_min = 0
        self._image_saved = None

    def get_feature(self, context):
        frame = context['engine']['frame'][300:720]  # 一定時間、画面半分を見る
        frame_gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
        frame_gray_small = cv2.resize(frame_gray, (128, 42))
        frame_gray_small_1d = np.reshape(frame_gray_small, (-1))

        f_max = np.average(frame_gray_small_1d)
        f_min = np.average(frame_gray_small_1d)

        # print("max %3.1f min %3.1f" % (f_max, f_min))

        return frame_gray_small_1d, f_max, f_min

    def on_game_finish(self, context):
        f_img, f_max, f_min = self.get_feature(context)
        self._switch_state(self._state_tracking)

    def on_result_judge(self, context):
        self.reset()
        self._switch_state(self._state_default)

    def on_result_scoreboard(self, context):
        self.reset()
        self._switch_state(self._state_default)

    def _state_default(self, context):
        return

    def _state_tracking(self, context):
        # FIXME: 経過時間でシーンを抜けるほうが安全

        frame = context['engine']['frame']

        if frame is None:
            return False

        if self.is_another_scene_matched(context, 'Spl2GameFinish'):
            return False

        f_img, f_max, f_min = self.get_feature(context)

        # Phase 1:
        # 一度真っ暗になる。真っ暗になってから戻ってきたら
        # このブロックを抜ける

        if (f_max < self._smallest_max):
            self._smallest_max = f_max
            return False

        if (self._smallest_max > 50):
            return False

        # Phase 2:
        # 画面が明るくなっていく。このうち１番明るい画像が候補
        # 画像の変化がなくなったら確定する

        f_img_last = self._last_img_bar_b_i16
        f_img = np.array(f_img, dtype=np.int16)
        self._last_img_bar_b_i16 = f_img

        if (self._image_saved is not None):

            img_diff = np.max(abs(f_img - f_img_last))
            self._last_img_bar_b_i16 = f_img
            trigger = (img_diff < 20)

            if trigger:
                context['game']['image_map'] = self._image_saved
                self._call_plugins('on_result_map')
                self.reset()
                self._switch_state(self._state_default)
                return False

        # 画面が明るくなったなら候補として保存
        if (self._highest_min < f_min):
            self._image_saved = copy.deepcopy(context['engine']['frame'])
            # cv2.imshow('map', self._image_saved)
            self._highest_min = f_min

        return False

    def _init_scene(self, debug=False):
        pass


if __name__ == "__main__":
    Spl2ResultMap.main_func()
