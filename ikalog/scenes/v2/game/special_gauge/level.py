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
import numpy as np

from ikalog.scenes.scene import Scene
from ikalog.utils import *

"""
FIXME:
This core algorhythm is compatible with Splatoon and Splatoon 2
"""
_mask_level = None
_mask_level_pixels = None


def _initialize_mask_image():
    global _mask_level
    _mask_level = np.zeros((102, 102, 3), dtype=np.uint8)
    cv2.circle(_mask_level, (51, 51), 48, (255, 255, 255), 3)
    _mask_level[0:55, 0:55] = np.zeros((55, 55, 3), dtype=np.uint8)

    global _mask_level_pixels
    _mask_level_pixels = np.sum(_mask_level[:, :, 0]) / 255


def calcurate_special_level(img):
    assert img.shape[0] == 102
    assert img.shape[1] == 102

    img_hsv = cv2.cvtColor(img, cv2.COLOR_BGR2HSV)
    img_filtered = img_hsv[:, :, 2]
    img_filtered[img_filtered <= 64] = 0
    img_masked = img_filtered & _mask_level[:, :, 0]
    cv2.imshow('level', img_masked)

    pixels = np.sum(img_masked) / 255
    value = int(pixels / _mask_level_pixels * 100)

    return value


def is_special_charged(frame):
    img_white = matcher.MM_WHITE()(frame[34:34 + 102, 1117:1117 + 102, :])
    img_white_masked = img_white & self._mask_gauge[:, :, 0]
    white_score = np.sum(img_white_masked / 255)
    charged = (white_score > 0)

_initialize_mask_image()

"""
Splatoon 2 specific code here
"""


class V2GameSpecialGaugeLevel(StatefulScene):

    def reset(self):
        super(V2GameSpecialGaugeLevel, self).reset()
        self._last_event_msec = - 100 * 1000

    def match_no_cache(self, context):
        """
        This scene only works when special gauge is shown
        """
        matched = self.is_another_scene_matched(context, 'V2GameSubAndSpecial')
        if not matched:
            return False

        frame = context['engine']['frame']
        img = frame[32:32 + 102, 1136:1136 + 102, :]
        value = calcurate_special_level(img)

        last_value = context['game'].get('special_gauge', None)
        last_charged = context['game'].get('special_gauge_charged', False)

        # FIXME: "chagrged" not implemented for Splatoon 2
        charged = False
        if 0:  # value > 95:
            img_white = matcher.MM_WHITE()(
                frame[34:34 + 102, 1117:1117 + 102, :])
            img_white_masked = img_white & self._mask_gauge[:, :, 0]
            white_score = np.sum(img_white_masked / 255)
            charged = (white_score > 0)

        if value != last_value:
            context['game']['special_gauge'] = value
            self._call_plugins('on_game_special_gauge_update')

        if (not last_charged) and (charged):
            self._call_plugins('on_game_special_gauge_charged')
        context['game']['special_gauge_charged'] = charged

        return True

    def _analyze(self, context):
        pass

    def _init_scene(self, debug=False):
        pass

if __name__ == "__main__":
    V2GameSpecialGaugeLevel.main_func()
