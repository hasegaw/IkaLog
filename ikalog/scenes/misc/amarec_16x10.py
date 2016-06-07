#!/usr/bin/env python3
# -*- coding: utf-8 -*-
#
#  IkaLog
#  ======
#  Copyright (C) 2016 Takeshi HASEGAWA
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

from ikalog.utils import *
from ikalog.scenes.stateful_scene import StatefulScene


class Amarec16x10Warning(StatefulScene):

    def _is_16x10(self, context):
        if self.is_another_scene_matched(context, 'GameTimerIcon'):
            return False

        if self.is_another_scene_matched(context, 'Blank'):
            return False

        img = context['engine']['frame']
        geom = img.shape
        w = 64

        r = np.sum(img[:, w, :])
        l = np.sum(img[:, geom[1] - w: w, :])

        return (r + l) == 0

    def _state_default(self, context):
        matched = self._is_16x10(context)
        if matched:
            self._switch_state(self._state_tracking)
            self._call_plugins(
                'on_amarec16x10_warning',
                params={'enabled': True},
            )

        return matched

    def _state_tracking(self, context):
        matched = self._is_16x10(context)
        if not matched:
            self._switch_state(self._state_default)
            self._call_plugins(
                'on_amarec16x10_warning',
                params={'enabled': False},
            )

        return matched

    def _analyze(self, context):
        pass

    def _init_scene(self, debug=False):
        pass

if __name__ == "__main__":
    Amarec16x10Warning.main_func()
