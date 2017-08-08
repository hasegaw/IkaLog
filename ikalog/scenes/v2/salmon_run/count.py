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
import sys

import cv2

from ikalog.scenes.stateful_scene import StatefulScene
from ikalog.ml.text_reader import TextReader
from ikalog.utils import *

import re


def get_salmonrun_from_context(context):
    if not 'salmon_run' in context:
        context['salmon_run'] = {}
    return context['salmon_run']


class SalmonRunTimeCounter(StatefulScene):

    def reset(self):
        super(SalmonRunTimeCounter, self).reset()

        self._last_event_msec = - 100 * 1000

    def _get_egg_count_from_frame(self, context):
        img_count = context['engine']['frame'][66:66 + 33, 187:187 + 85]
        cv2.imshow('NormaCounter2', img_count)

        img_count_hsv = cv2.cvtColor(img_count, cv2.COLOR_BGR2HSV)
        img_count_gray = img_count_hsv[:, :, 2]
        img_count_gray[img_count_hsv[:, :, 1] > 30] = 0

        #img_count_gray = cv2.cvtColor(img_count, cv2.COLOR_BGR2GRAY)
        img_count_gray[img_count_gray < 200] = 0
        img_count_gray[img_count_gray > 0] = 255

        count_str = self._tr.read_char(img_count_gray)
        if count_str is None:
            return False

        m = re.match(r'^([0-9])+/([0-9+])$', count_str)
        if m is None:
            return False

        self._eggs_earned, self._eggs_target = int(m.group(1)), int(m.group(2))
        print('%s: eggs %d/%d' % (self, self._eggs_earned, self._eggs_target))

        return True

    def _state_default(self, context):
        if (not self.is_another_scene_matched(context, 'SalmonRunNorma')):
            return False

        r1 = self._get_egg_count_from_frame(context)
        if not r1:
            return False

        img_count = context['engine']['frame'][66:66 + 33, 57:57 + 61]
        cv2.imshow('SalmonRunTimeCounter', img_count)
        img_count_gray = cv2.cvtColor(img_count, cv2.COLOR_BGR2GRAY)
        img_count_gray[img_count_gray < 200] = 0
        img_count_gray[img_count_gray > 0] = 255

        count_str = self._tr.read_char(img_count_gray)
        if count_str is None:
            return False

        try:
            count = int(count_str)
        except ValueError:
            return False

        print(self, ':', count)

    def check_timeout(self, context):
        # 3000ms 以内の非マッチはチャタリングとみなす
        if self.matched_in(context, 3000):
            return False

        self._last_event_msec = context['engine']['msec']
        self._switch_state(self._state_default)
        print('%s: force default state')
        return False

    def dump(self, context):
        pass

    def _analyze(self, context):
        pass

    def _init_scene(self, debug=False):
        self._tr = TextReader()


if __name__ == "__main__":
    SalmonRunTimeCounter.main_func()
