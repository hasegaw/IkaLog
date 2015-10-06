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


class InGame(object):
    # 720p サイズでの値
    timer_left = 60
    timer_width = 28
    timer_top = 28
    timer_height = 34

    # 生存イカの検出
    meter_left = 399
    meter_top = 55
    meter_width = 485
    meter_height = 1

    def lives(self, context):
        if not context['engine']['inGame']:
            return None, None

        img = context['engine']['frame'][self.meter_top:self.meter_top +
                                         self.meter_height, self.meter_left:self.meter_left + self.meter_width]
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

        team1 = np.sort(team1)
        team2 = np.sort(team2)

        # 目の部分が白かったら True なマスクをつくる
        img_eye = context['engine']['frame'][
            44:50, self.meter_left:self.meter_left + self.meter_width]
        img_eye_hsv = cv2.cvtColor(img_eye, cv2.COLOR_BGR2HSV)
        eye_white_mask_s = cv2.inRange(img_eye_hsv[:, :, 1], 0, 48)
        eye_white_mask_v = cv2.inRange(img_eye_hsv[:, :, 2], 200, 256)
        eye_white_mask = np.minimum(eye_white_mask_s, eye_white_mask_v)
        a = []
        team1_color = None
        team2_color = None

        for i in team1:
            eye_score = np.sum(eye_white_mask[:, i - 4: i + 4]) / 255
            alive = eye_score > 1
            a.append(alive)

            if alive:
                team1_color = img[0, i]  # BGR
                team1_color_hsv = img_hsv[0, i]

            cv2.rectangle(context['engine']['frame'], (self.meter_left +
                                                       i - 4,  44), (self.meter_left + i + 4, 50), (255, 255, 255), 1)

        b = []
        for i in team2:
            eye_score = np.sum(eye_white_mask[:, i - 4: i + 4]) / 255
            alive = eye_score > 1
            b.append(alive)

            if alive:
                team2_color = img[0, i]  # BGR
                team2_color_hsv = img_hsv[0, i]

            cv2.rectangle(context['engine']['frame'], (self.meter_left +
                                                       i - 4,  44), (self.meter_left + i + 4, 50), (255, 255, 255), 1)
        # print("色: 味方 %d 敵 %d" % (team1_color, team2_color))
        # print("味方 %s 敵 %s" % (a,b))
        # cv2.imshow('yagura_gray', img_gray2)
        # cv2.imshow('yagura_gray2', img_gray3)
        # cv2.imshow('eyes', eye_white_mask)

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

            callPlugins = context['engine']['service']['callPlugins']
            callPlugins('on_game_team_color')

        return (a, b)

    def matchTimerIcon(self, context):
        img = IkaUtils.cropImageGray(
            context['engine'][
                'frame'], self.timer_left, self.timer_top, self.timer_width, self.timer_height
        )

        return self.mask_timer.match(context['engine']['frame'])

    def matchPaintScore(self, context):
        x_list = [938, 988, 1032, 1079]

        paint_score = 0
        for x in x_list:
            # Extract a digit.
            img = context['engine']['frame'][33:33 + 41, x:x + 37, :]

            # Check if the colr distribution in in expected range.
            img_gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
            hist = cv2.calcHist([img_gray], [0], None, [5], [0, 256])
            try:
                black_raito = hist[0] / np.sum(hist)
                black_white_raito = (hist[0] + hist[4]) / np.sum(hist)
            except ZeroDivisionError:
                score = 0

            if (black_raito < 0.5) or (0.8 < black_raito) or \
                    (black_white_raito < 0.8):
                # Seems not to be a white character on black background.
                return None

            # Recoginize a digit.
            digit = self.number_recoginizer.match_digits(
                img,
                num_digits=(1, 1),
                char_width=(11, 40),
                char_height=(28, 33),
            )

            if digit is None:
                return None

            paint_score = (paint_score * 10) + digit

        # Set latest paint_score to the context.
        context['game']['paint_score'] = \
            max(context['game'].get('paint_score', 0), paint_score)

    # FixMe
    _last_killed = 0

    def matchKilled(self, context):
        img_gray = cv2.cvtColor(context['engine']['frame'][
                                :, 502:778], cv2.COLOR_BGR2GRAY)
        ret, img_thresh = cv2.threshold(img_gray, 90, 255, cv2.THRESH_BINARY)

        killed_y = [652, 652 - 40, 652 - 80, 652 - 120]  # たぶん...。
        killed = 0

        list = []
        for n in range(len(killed_y)):
            y = killed_y[n]
            box = img_thresh[y:y + 30, :]
            r = self.mask_killed.match(box)

            if r:
                list.append(n)

        return len(list)

    def matchGoSign(self, context):
        return self.mask_goSign.match(context['engine']['frame'])

    def matchDead(self, context):
        return self.mask_dead.match(context['engine']['frame'])

    def match(self, context):
        context['engine']['inGame'] = self.matchTimerIcon(context)

        if not context['engine']['inGame']:
            return False

        callPlugins = context['engine']['service']['callPlugins']
        msec = context['engine']['msec']

        if not self in context['scenes']:
            context['scenes'][self] = {
                'lastGoSign': msec - 60 * 1000,
                'lastDead': msec - 60 * 1000,
                'lastKill': msec - 60 * 1000,
                'kills': 0,
            }

        context['scenes'][self]['lastTimerIcon'] = msec

        # 塗りポイント(ナワバリのみ)
        self.matchPaintScore(context)

        # ゴーサイン (60秒に1度まで)
        if (context['scenes'][self]['lastGoSign'] + 60 * 1000) < msec:
            if self.matchGoSign(context):
                callPlugins('on_game_go_sign')
                context['scenes'][self]['lastGoSign'] = msec

        # 誰かをキルしたか
        kills = self.matchKilled(context)
        if context['scenes'][self]['kills'] < kills:
            callPlugins('on_game_killed')
            context['scenes'][self]['kills'] = kills
            context['scenes'][self]['lastKill'] = msec
        else:
            # 品質が悪いムービーのチャタリング対策
            # 長すぎると連続キル検出をミスする可能性あり
            if (context['scenes'][self]['lastKill'] + 1 * 1000) < msec:
                context['scenes'][self]['kills'] = kills

        # 死亡状態（「復活まであとｎ秒」）
        if self.matchDead(context):
            if (context['scenes'][self]['lastDead'] + 5 * 1000) < msec:
                callPlugins('on_game_dead')
            context['scenes'][self]['lastDead'] = msec
        return True

    def __init__(self):
        self.mask_timer = IkaMatcher(
            self.timer_left, self.timer_top, self.timer_top, self.timer_height,
            img_file='masks/ingame_timer.png',
            threshold=0.7,
            orig_threshold=0.7,
            false_positive_method=IkaMatcher.FP_BACK_IS_BLACK,
            pre_threshold_value=230,
            label='timer_icon',
            debug=False,
        )

        self.mask_goSign = IkaMatcher(
            1280 / 2 - 420 / 2, 130, 420, 170,
            img_file='masks/ui_go.png',
            threshold=0.98,
            orig_threshold=0.5,
            pre_threshold_value=240,
            label='Go!',
        )

        # mask_killed
        # 高画質動画なら threshold = 0.90 でいける
        # ビットレートが低いと threshold = 0.80 か
        # ビットレートが低い場合はイベントのチャタリング対策なども必要
        self.mask_killed = IkaMatcher(
            0, 0, 50, 30,
            img_file='masks/ui_killed.png',
            threshold=0.80,
            orig_threshold=0.10,
            false_positive_method=IkaMatcher.FP_BACK_IS_BLACK,
            pre_threshold_value=90,
            label='killed',
            debug=False
        )

        self.mask_dead = IkaMatcher(
            1057, 648, 140, 40,
            img_file='masks/ui_dead.png',
            threshold=0.8,
            orig_threshold=0.3,
            pre_threshold_value=220,
            label='dead',
        )

        self.number_recoginizer = NumberRecoginizer()

if __name__ == "__main__":
    print(sys.argv)
    target = cv2.imread(sys.argv[1])

    context = {
        'engine': {'frame': target},
        'game': {},
    }

    obj = InGame()

    r = obj.matchTimerIcon(context)

    print(r)
