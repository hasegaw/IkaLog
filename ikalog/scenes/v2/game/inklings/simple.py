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

import copy
import re
import traceback
import time
import numpy as np

import cv2

from ikalog.ml.classifier import ImageClassifier
from ikalog.ml.text_reader import TextReader
from ikalog.scenes.stateful_scene import StatefulScene
from ikalog.inputs.filters import OffsetFilter
from ikalog.utils import *

from ikalog.scenes.v2.game.inklings.extract import extract_players

class Spl2GameInklings(StatefulScene):

    def _list2bitmap(self, list1, list2):
        l = list1.copy()
        l.extend(list2)

        bitmap = 0
        for i in range(len(l)):
            bitmap = bitmap + bitmap + (1 if l[i] else 0)

        return bitmap

    def _read_int(self, img):
        # cv2.imshow('read char', img)
        cv2.waitKey()

        img = cv2.resize(img, (img.shape[1] * 3, img.shape[0] * 3))

        img_hsv = cv2.cvtColor(img, cv2.COLOR_BGR2HSV)
        img_gray = img_hsv[:, :, 2]
        img_gray[img_gray < 200] = 0
        img_gray[img_hsv[:, :, 1] > 30] = 0
        img_gray[img_gray > 0] = 255

        val_str, val_int = None, None
        img_bgr = cv2.cvtColor(img_gray, cv2.COLOR_GRAY2BGR)
        if 1:
            val_str = self._tr.read_char(img_gray)
            print('Read: %s' % val_str)

        try:
            val_int = int(val_str)
        except:
            pass

        #cv2.imshow('%s' % val_str, img_bgr)
        # cv2.waitKey(1000)
        return val_int

    def _read_str(self, img):
        #cv2.imshow('read char', img)

        img = cv2.resize(img, (img.shape[1] * 3, img.shape[0] * 3))

        img_hsv = cv2.cvtColor(img, cv2.COLOR_BGR2HSV)
        img_gray = img_hsv[:, :, 2]
        img_gray[img_gray < 200] = 0
        img_gray[img_hsv[:, :, 1] > 30] = 0
        img_gray[img_gray > 0] = 255

        val_str, val_int = None, None
        img_bgr = cv2.cvtColor(img_gray, cv2.COLOR_GRAY2BGR)
        if 1:
            val_str = self._tr.read_char(img_gray)
            print('Read: %s' % val_str)

        #cv2.imshow('%s' % val_str, img_bgr)
        # cv2.waitKey(1000)
        return val_str

    def analyze(self, context):
        return

    def reset(self):
        super(Spl2GameInklings, self).reset()

        self._last_event_msec = - 100 * 1000
        self._match_start_msec = - 100 * 1000
        self._last_bitmap = None
        self._last_bitmap_special = None

        self._last_frame = None
        self._diff_pixels = []

    def check_match(self, context):
        # return self.is_another_scene_matched(context, 'GameTimerIcon')
        frame = context['engine']['frame']

        if frame is None:
            return False
        return True
        



    def _state_default(self, context):
        # pass matching in some scenes.
        frame = context['engine']['frame']
        if frame is None:
            return False

        matched = self.check_match(context)

        if matched:
            self._switch_state(self._state_tracking)
        return matched

    def _state_tracking(self, context):
        frame = context['engine']['frame']

        matched = self.check_match(context)
        escaped = not self.matched_in(context, 1000)

        if escaped:
            self._switch_state(self._state_default)

        if matched:
            players = extract_players(frame, context)
            team1 = players[0:4]
            team2 = players[4:8]

            team1_alive = [1 if e.get('alive') else 0 for e in team1 if e is not None]
            team2_alive = [1 if e.get('alive') else 0 for e in team2 if e is not None]

            team1_special = [1 if e.get('special') else 0 for e in team1 if e is not None]
            team2_special = [1 if e.get('special') else 0 for e in team2 if e is not None]

            context['game']['inkling_state'] = [
                team1_alive,
                team2_alive,
                team1_special,
                team2_special
            ]

            bitmap = self._list2bitmap(team1_alive, team2_alive)
            if self._last_bitmap != bitmap:
                self._call_plugins('on_game_inkling_state_update')
                self._last_bitmap = bitmap
                IkaUtils.add_event(
                    context, 'inklings', context['game']['inkling_state'])
                # for i, p in enumerate(players):
                #     cv2.imwrite("pimg/p%s/%s.png" % (i, time.time()), p['img_weapon'])
                #     cv2.imwrite("pimg/p%s/full_%s.png" % (i, time.time()), p['full'])

            bitmap_special = self._list2bitmap(team1_special, team2_special)
            if self._last_bitmap_special != bitmap_special:
                self._call_plugins('on_game_special_state_update')
                self._last_bitmap_special = bitmap_special
                IkaUtils.add_event(
                    context, 'inklings', context['game']['inkling_state'])

        return matched

    def dump(self, context):
        print('--------')

        for e in context['game']['inkling_state']:
            print(e)

    def _init_scene(self, debug=False):
        self._tr = TextReader()


if __name__ == "__main__":
    Spl2GameInklings.main_func()
