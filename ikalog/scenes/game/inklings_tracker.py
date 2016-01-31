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

from ikalog.scenes.scene import Scene
from ikalog.utils import *

class InklingsTracker(Scene):
    meter_left = 399
    meter_top = 55
    meter_width = 485
    meter_height = 1

    def reset(self):
        super(InklingsTracker, self).reset()
        self.last_state = ''

    def match_no_cache(self, context):
        if self.is_another_scene_matched(context, 'GameTimerIcon') == False:
            return False

        frame = context['engine']['frame']

        if frame is None:
            return False

        img = frame[
            self.meter_top:self.meter_top + self.meter_height,
            self.meter_left:self.meter_left + self.meter_width
        ]
        img_hsv = cv2.cvtColor(img, cv2.COLOR_BGR2HSV)
        img2 = cv2.resize(img, (self.meter_width, 100))
        # for i in range(2):
        #     img2[20:40,:, i] = cv2.resize(img_hsv[:,:,0], (self.meter_width, 20))
        #     img2[40:60,:, i] = cv2.resize(img_hsv[:,:,1], (self.meter_width, 20))
        #     img2[60:80,:, i] = cv2.resize(img_hsv[:,:,2], (self.meter_width, 20))
        #
        # cv2.imshow('yagura',     img2)
        # cv2.imshow('yagura_hsv', cv2.resize(img_hsv, (self.meter_width, 100)))

        # VS 文字の位置（白）を検出する (s が低く v が高い)
        white_mask_s = cv2.inRange(img_hsv[:, :, 1], 0, 8)
        white_mask_v = cv2.inRange(img_hsv[:, :, 2], 248, 256)
        white_mask = np.minimum(white_mask_s, white_mask_v)

        x_list = np.arange(self.meter_width)
        vs_x = np.extract(white_mask > 128, x_list)

        vs_xPos = np.average(vs_x)  # VS があるX座標の中心がわかった

        # print(vs_xPos)

        # 明るい白以外を検出する (グレー画像から)
        img_gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
        img_gray2 = cv2.resize(img_gray, (self.meter_width, 20))
        img_gray3 = cv2.inRange(img_gray2, 48, 256)

        team1 = []
        team2 = []

        try:
            # 左チーム
            x = vs_xPos - 20
            x2 = x
            direction = -3
            for i in range(4):
                while img_gray3[0, x] < 128:
                    x2 = x
                    x = x + direction

                while img_gray3[0, x] > 128:
                    x = x + direction

                x1 = x
                # プレイヤー画像は x1:x2 の間にある
                squid_xPos = int((x1 + x2) / 2)
                #print(x1, squid_xPos, x2)
                team1.append(squid_xPos)

            # 右チーム
            x = vs_xPos + 20
            x1 = x
            direction = 3
            for i in range(4):
                while img_gray3[0, x] < 128:
                    x1 = x
                    x = x + direction

                while img_gray3[0, x] > 128:
                    x = x + direction

                x2 = x
                # プレイヤー画像は x1:x2 の間にある
                squid_xPos = int((x1 + x2) / 2)
                #print(x1, squid_xPos, x2)
                team2.append(squid_xPos)
        except IndexError:
            return False

        team1 = np.sort(team1)
        team2 = np.sort(team2)

        # 目の部分が白かったら True なマスクをつくる
        img_eye = frame[
            44:50,
            self.meter_left:self.meter_left + self.meter_width
        ]
        img_eye_hsv = cv2.cvtColor(img_eye, cv2.COLOR_BGR2HSV)
        eye_white_mask_s = cv2.inRange(img_eye_hsv[:, :, 1], 0, 48)
        eye_white_mask_v = cv2.inRange(img_eye_hsv[:, :, 2], 200, 256)
        eye_white_mask = np.minimum(eye_white_mask_s, eye_white_mask_v)
        team1_color = None
        team2_color = None
        a = []
        b = []

        for i in team1:
            eye_score = np.sum(eye_white_mask[:, i - 4: i + 4]) / 255
            alive = bool(eye_score > 1)
            a.append(alive)

            if alive:
                team1_color = img[0, i]  # BGR
                team1_color_hsv = img_hsv[0, i]

            cv2.rectangle(
                frame,
                (self.meter_left + i - 4,  44),
                (self.meter_left + i + 4, 50),
                (255, 255, 255),
                1
            )

        for i in team2:
            eye_score = np.sum(eye_white_mask[:, i - 4: i + 4]) / 255
            alive = bool(eye_score > 1)
            b.append(alive)

            if alive:
                team2_color = img[0, i]  # BGR
                team2_color_hsv = img_hsv[0, i]

            cv2.rectangle(
                frame,
                (self.meter_left + i - 4,  44),
                (self.meter_left + i + 4, 50),
                (255, 255, 255),
                1
            )

        context['game']['inkling_state'] = [a, b]

        hasTeamColor = ('team_color_bgr' in context['game'])

        if (not team1_color is None) and (not team2_color is None) and not hasTeamColor:
            context['game']['team_color_bgr'] = [
                team1_color,
                team2_color
            ]
            context['game']['team_color_hsv'] = [
                team1_color_hsv,
                team2_color_hsv
            ]
            self._call_plugins('on_game_team_color')

        state = self._state_to_string(a) + ' ' + self._state_to_string(b)
        if state != self.last_state:
            self.last_state = state
            # self.dump(context)
            self._call_plugins('on_game_inkling_state_update')

        return True

    def _analyze(self, context):
        pass

    def dump(self, context):
        print('inkling state: %s vs %s' % (
            self._state_to_string(context['game']['inkling_state'][0]),
            self._state_to_string(context['game']['inkling_state'][1])
        ))

    def _state_to_string(self, states):
        ret = ''
        for i in range(4):
            if i < len(states):
                ret = ret + ('1' if states[i] else '0')
            else:
                ret = ret + '_'
        return ret
