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

from ikalog.scenes.scene import Scene
from ikalog.utils import *


class Spl2SalmonRunWaveFinish(Scene):

    def reset(self):
        super(Spl2SalmonRunWaveFinish, self).reset()

        self._last_event_msec = - 100 * 1000

    def on_salmonrun_mr_grizz_comment(self, context, params):
        if params['text_id'] in ('wave_finish', 'wave_finish3'):
            self._call_plugins('on_salmonrun_wave_finish')

    def match_no_cache(self, context):
        return False

    def dump(self, context):
        pass

    def _analyze(self, context):
        pass

    def _init_scene(self, debug=False):
        pass


if __name__ == "__main__":
    Spl2SalmonRunWaveFinish.main_func()
