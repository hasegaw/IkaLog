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
import os

import cv2
import numpy as np

from ikalog.scenes.scene import Scene
from ikalog.utils import *
import copy


class GameCommunication(Scene):

    def reset(self):
        super(GameCommunication, self).reset()
        self._msec_last_booyah = -10 * 1000
        self._msec_last_comeon = -10 * 1000

    # for testing...
    def _generate_test_image(self, context):
        img = np.zeros((720, 1280), dtype=np.uint8)
        samples = 50

        x_max = int(1280 / self.img_booyah.shape[1]) - 2

        for i in range(samples):
            if i < 1:
                continue

            # Resized image
            dx = int(self.img_booyah.shape[1] / samples * i)
            dy = int(self.img_booyah.shape[0] / samples * i)
            template_small = cv2.resize(self.img_booyah, (dx, dy))

            # Position
            cx = int(i % x_max + 1) * self.img_booyah.shape[1]
            cy = int(i / x_max + 1) * self.img_booyah.shape[0]

            img[cy: cy + dy, cx: cx + dx] = template_small

        img = cv2.resize(img, (640, 360))
        context['engine']['frame'] = cv2.cvtColor(img, cv2.COLOR_GRAY2BGR)

    def max_pooling_2d(self, img, xy=(2, 2)):
        x, y = xy
        oh, ow = img.shape
        hw = int(ow / x)
        hh = int(oh / y)
        img = img[:hh * y, :hw * x]
        oh, ow = img.shape

        img_360p = np.max(img.reshape((oh, hw, x)),
                          axis=2).T.reshape((hw, hh, y))
        img_360p = np.max(img_360p, axis=2).T
        return img_360p

    def match_phase1(self, context):
        frame = context['engine']['frame']
        img_720p = matcher.MM_WHITE().evaluate(frame)
        img_360p = self.max_pooling_2d(img_720p)

        result_36p = {
            'booyah': np.zeros((36, 64)),
            'comeon': np.zeros((36, 64)),
        }

        for mask in self.masks:
            template = mask['image']
            res = cv2.matchTemplate(img_360p, template, cv2.TM_CCOEFF_NORMED)
            threshold = 0.8
            res[res < threshold] = 0
            img_36p = self.max_pooling_2d(res, (10, 10))
            if 0:
                cv2.imshow('36p', cv2.resize(img_36p, (640, 360)))
                cv2.waitKey(100)
            result_36p[mask['event']][:img_36p.shape[0], :img_36p.shape[1]] += img_36p

        is_already_matched = \
            self.matched_in(context, 5 * 1000, attr='_msec_last_booyah')
        is_matched = np.max(result_36p['booyah']) > 0
        if (not is_already_matched) and is_matched:
            self._call_plugins('on_game_booyah')
            self._msec_last_booyah = context['engine']['msec']

        is_already_matched = \
            self.matched_in(context, 5 * 1000, attr='_msec_last_comeon')
        is_matched = np.max(result_36p['comeon']) > 0
        if (not is_already_matched) and is_matched:
            self._call_plugins('on_game_comeon')
            self._msec_last_comeon = context['engine']['msec']

#        cv2.imshow('36p', cv2.resize(result_36p, (640, 360)))
#        cv2.waitKey(100)

    def match_no_cache(self, context):
        # ゲーム中/OOB中にのみ有効
        if not self.find_scene_object('GameTimerIcon').matched_in(context, 3 * 1000):
            return False

        self.match_phase1(context)

    def dump(self, context):
        pass

    def _analyze(self, context):
        pass

    # FIXME: Move to utility class
    def _find_image_file(self, img_file=None, languages=None):
        if languages is None:
            languages = Localization.get_game_languages()

        if languages is not None:
            if not isinstance(languages, list):
                languages = [lang]

            for lang in languages:
                f = os.path.join(
                    IkaUtils.baseDirectory(),
                    'masks',
                    lang,
                    img_file
                )
                if os.path.exists(f):
                    return f

        f = os.path.join(IkaUtils.baseDirectory(), 'masks', img_file)
        if os.path.exists(f):
            return f

        f = os.path.join(IkaUtils.baseDirectory(), img_file)
        if os.path.exists(f):
            return f

        f = os.path.join(IkaUtils.baseDirectory(), 'masks', 'ja', img_file)
        if os.path.exists(f):
            IkaUtils.dprint('%s: mask %s: using ja version' % \
                (self, img_file))
            return f

        raise Exception('Could not find image file %s (lang %s)' % \
            (img_file, lang))

    def _init_scene(self, debug=False):
        self.img_booyah = cv2.imread(self._find_image_file('booyah.png'), 0)
        self.img_comeon = cv2.imread(self._find_image_file('comeon.png'), 0)

        bh, bw = self.img_booyah.shape
        ch, cw = self.img_comeon.shape
        self.masks = [
            {'event': 'booyah', 'image': cv2.resize(
                self.img_booyah, (int(bw * 0.33), int(bh * 0.33)))},
            {'event': 'booyah', 'image': cv2.resize(
                self.img_booyah, (int(bw * 0.4), int(bh * 0.4)))},
            {'event': 'booyah', 'image': cv2.resize(
                self.img_booyah, (int(bw * 0.5), int(bh * 0.5)))},

            {'event': 'comeon', 'image': cv2.resize(
                self.img_comeon, (int(cw * 0.33), int(ch * 0.33)))},
            {'event': 'comeon', 'image': cv2.resize(
                self.img_comeon, (int(cw * 0.4), int(ch * 0.4)))},
            {'event': 'comeon', 'image': cv2.resize(
                self.img_comeon, (int(cw * 0.5), int(ch * 0.5)))},
        ]

if __name__ == "__main__":
    GameCommunication.main_func()
