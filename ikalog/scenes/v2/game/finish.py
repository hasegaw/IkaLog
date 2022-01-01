from PIL import ImageFont, ImageDraw, Image
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

import sys
import cv2
import time
import numpy as np

from ikalog.ml.classifier import ImageClassifier
from ikalog.utils import *
from ikalog.scenes.scene import Scene


class Spl2GameFinish(Scene):

    def reset(self):
        super(Spl2GameFinish, self).reset()

        self._last_event_msec = - 100 * 1000


    def match_no_cache(self, context):
        if self.matched_in(context, 60 * 1000, attr='_last_event_msec'):
            return False

        # if not self.find_scene_object('Spl2GameSession').matched_in(context, 20 * 1000):
        #     return False

        # if self.is_another_scene_matched(context, 'Spl2GameSession'):
        #     return False

        self._call_plugins('get_neutral_hue')
        frame = context['engine']['frame']
        
        # TODO: Alecat: remove colour based dependency
        # Find the areas of the image that match the neutral colour and compare them with the mask
        hue = context['game'].get('neutral_color_hue', 152/2)
        finish_strip_by_color = matcher.MM_COLOR_BY_HUE(
            hue=(hue - 10, hue + 10), visibility=(100, 255))(frame)

        matched = self._mask.match(finish_strip_by_color)

        matched_predict = self._c.predict_frame(frame) >= 0
        if matched_predict:
            pass
            # print("ML MODEL FOUND THE FINISH FRAME")
        if not matched:
            return False

        context['game']['end_time'] = IkaUtils.getTime(context)
        context['game']['end_offset_msec'] = context['engine']['msec']

        self._call_plugins('on_game_finish')
        self._last_event_msec = context['engine']['msec']

        return True

    def _analyze(self, context):
        pass

    def _init_scene(self, debug=False):
        self._c = ImageClassifier()
        self._c.load_from_file('data/spl2/spl2.game.finish.dat')
        self._mask = IkaMatcher(
            0, 0, 1280, 720,
            img_file='game_finish.png',
            threshold= 0.9,
            orig_threshold= 0.05,
            bg_method=matcher.MM_BLACK(visibility=(0, 215)),
            fg_method=matcher.MM_NOT_BLACK(),
            label='finish',
            call_plugins=self._call_plugins,
            debug=False
        )

if __name__ == "__main__":
    Spl2GameFinish.main_func()
