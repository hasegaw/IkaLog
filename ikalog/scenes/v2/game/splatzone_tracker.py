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
import numpy as np

from ikalog.utils import *
from ikalog.scenes.scene import Scene
from ikalog.ml.text_reader import TextReader


class SplatzoneTracker(Scene):

    def reset(self):
        super(SplatzoneTracker, self).reset()

        self._counter1 = {
            'last_internal_update': -100 * 1000,
            'last_update': -100 * 1000,
            'value': 100,
            'injury_value': None,
            'last_injury_update': -100 * 1000
        }
        self._counter2 = {
            'last_internal_update': -100 * 1000,
            'last_update': -100 * 1000,
            'value': 100,
            'injury_value': None,
            'last_injury_update': -100 * 1000
        }

    def analyzeCounter(self, context, counter, img_counter):
        # n = self.number_recoginizer.match_digits(
        #     img_counter,
        # )

        
        img_hsv = cv2.cvtColor(img_counter, cv2.COLOR_BGR2HSV)
        img_gray = img_hsv[:, :, 2]
        img_gray[img_gray < 200] = 0
        img_gray[img_hsv[:, :, 1] > 30] = 0
        img_gray[img_gray > 0] = 255
        try:
            n = self._tr.read_int(img_gray)
        except:
            return False, 0

        print(n)
        if n is None:
            return False, 0

        msec = context['engine']['msec']

        r_valid = (n + 1 == counter['value']) or (n == counter['value'])
        r_force_update = (counter['last_internal_update'] + 3000 < msec)

        if r_force_update:
            self._call_plugins('on_game_splatzone_counter_resync')

        if not (r_valid or r_force_update):
            return False, 0

        diff = (n - counter['value'])
        counter['value'] = n
        counter['last_internal_update'] = msec
        if (diff != 0):
            counter['last_update'] = msec
            # カウントが進んでいるタイミングではロスタイムは無いはず!
            counter['injury_value'] = None
            counter['last_injury_update'] =  msec
        return True, diff

    def analyzeLossCounter(self, context, counter, img_injury):
        # カウントが進んでいる間はロスタイムはないはず
        if not (counter['last_update'] + 2000 < context['engine']['msec']):
            return False, 0

        # マスクを用意しておいて使うべき？
        img_injury_hsv = cv2.cvtColor(img_injury, cv2.COLOR_BGR2HSV)
        img_injury_mono = cv2.inRange(img_injury_hsv[:, :, 1], 0, 32)
        img_injury_mono[img_injury_mono > 1] = 1
        pixels = img_injury_mono.shape[0] * img_injury_mono.shape[1]
        mono_raito = np.sum(img_injury_mono) / (pixels)

        img_last_injury = counter.get('img_injury', None)
        img_last_injury_i16 = counter.get('img_injury_i16', None)

        img_injury_i16 = np.array(img_injury, np.int16)
        counter['img_injury'] = img_injury
        counter['img_injury_i16'] = img_injury_i16
        diff_pixels = None
        if img_last_injury_i16 is not None:
            img_white = \
                self._white_filter(img_injury) | \
                self._white_filter(img_last_injury)
            img_diff = abs(img_injury_i16 - img_last_injury_i16)
            img_diff_u8 = np.array(img_diff, np.uint8)
            img_diff_u8[img_diff_u8 < 16] = 0
            img_diff_u8[img_diff_u8 > 1] = 255
            img_diff_u8[img_white < 128] = 0
#            cv2.imshow('DIFF', img_diff_u8)
            img_diff_u8[img_diff_u8 > 1] = 255
            diff_pixels = np.sum(img_diff_u8)

        if (diff_pixels is None) or (diff_pixels > 20):
            return False, 0

        n = self.number_recoginizer.match_digits(
            img_injury,
        )
        # n = self._tr.read_int(img_injury)

        if n is None:
            return False, 0

        msec = context['engine']['msec']
        last_injury_value = counter['injury_value']

        r_new = (last_injury_value is None)
        r_valid = (not r_new) and \
            ((n + 1 == last_injury_value) or (n == last_injury_value))
        r_force_update = (counter['last_injury_update'] + 3000 < msec)

        if r_new:
            self._call_plugins('on_game_splatzone_injury_time')

        if r_force_update:
            self._call_plugins('on_game_splatzone_injury_counter_resync')

        if not (r_new or r_valid or r_force_update):
            return False, 0

        diff = 0
        if r_valid:
            diff = n - last_injury_value

        counter['injury_value'] = n
        counter['last_injury_update'] = msec

        return r_valid, diff

    def on_game_splatzone_we_lost(self, context):
        # Timer no longer pulses after losing the zone, so log scores + penalty
        print("we got it!")


    def match_no_cache(self, context):
        return False
        if self.is_another_scene_matched(context, 'GameTimerIcon') == False:
            return False

        rule_id = context['game']['rule']
        if rule_id != 'area':
            return False

        frame = context['engine']['frame']

        if frame is None:
            return False

        img_counter1 = frame[105:105 + 32, 540:540 + 67]
        img_counter2 = frame[105:105 + 32, 675:675 + 67]
        img_injury1 = context['engine']['frame'][145:145 + 30, 588:588 + 32]
        img_injury2 = context['engine']['frame'][145:145 + 30, 679:679 + 32]
        # cv2.imshow('counter1', img_counter1)
        # cv2.imshow('counter2', img_counter2)
        # cv2.imshow('loss1', img_injury1)
        # cv2.imshow('loss2', img_injury2)

        counter1 = self.analyzeCounter(context, self._counter1, img_counter1)
        counter2 = self.analyzeCounter(context, self._counter2, img_counter2)
        loss1 = self.analyzeLossCounter(context, self._counter1, img_injury1)
        loss2 = self.analyzeLossCounter(context, self._counter2, img_injury2)
        # print(loss1) #counter1, counter2, self._counter1['value'],
        # self._counter2['value'])

        context['game']['splatzone_my_team_counter'] = self._counter1
        context['game']['splatzone_counter_team_counter'] = self._counter2

        if (counter1[1] != 0) or (counter2[1] != 0) or (loss1[1] != 0) or (loss2[1] != 0):
            IkaUtils.add_event(
                context, 'splatzone', [self._counter1['value'],
                                       self._counter2['value']])
            self._call_plugins('on_game_splatzone_counter_update')

    def _analyze(self, context):
        pass

    def _init_scene(self, debug=False):
        self.number_recoginizer = character_recoginizer.NumberRecoginizer()
        self._tr = TextReader()
        self._white_filter = matcher.MM_WHITE()
        pass

if __name__ == "__main__":
    SplatzoneTracker.main_func()
