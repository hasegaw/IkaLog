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
from ikalog.IkaUtils import *

# Tracker the control tower, (or rainmaker)
#


class IkaScene_TowerTracker:
    # 720p サイズでの値
    tower_width = 580
    tower_left = 1280 / 2 - tower_width / 2
    tower_top = 78
    tower_height = 88

    tower_line_top = 93
    tower_line_height = 5

    def reset(self, context):
        context['game']['tower'] = {
            'pos': 0,
            'max': 0,
            'min': 0,
        }

    def towerPos(self, context):
        img = context['engine']['frame'][self.tower_line_top:self.tower_line_top +
                                         self.tower_line_height, self.tower_left:self.tower_left + self.tower_width]
        img2 = cv2.resize(img, (self.tower_width, 100))
        img_hsv = cv2.cvtColor(img, cv2.COLOR_BGR2HSV)
        for i in range(2):
            img2[20:40, :, i] = cv2.resize(
                img_hsv[:, :, 0], (self.tower_width, 20))
            img2[40:60, :, i] = cv2.resize(
                img_hsv[:, :, 1], (self.tower_width, 20))
            img2[60:80, :, i] = cv2.resize(
                img_hsv[:, :, 2], (self.tower_width, 20))

        # ゲージのうち信頼できる部分だけでマスクする
        img3 = np.minimum(img, self.ui_tower_mask)

        # 白い部分にいまヤグラ/ホコがある
        img3_hsv = cv2.cvtColor(img3, cv2.COLOR_BGR2HSV)
        white_mask_s = cv2.inRange(img3_hsv[:, :, 1], 0, 8)
        white_mask_v = cv2.inRange(img3_hsv[:, :, 2], 248, 256)
        white_mask = np.minimum(white_mask_s, white_mask_v)
        x_list = np.arange(self.tower_width)
        tower_x = np.extract(white_mask[3, :] > 128, x_list)
        tower_xPos = np.average(tower_x)

        # FixMe: マスクした関係が位置がずれている可能性があるので、適宜補正すべき

        xPos_pct = (tower_xPos - self.tower_width / 2) / \
            (self.tower_width * 0.86 / 2) * 100

        # あきらかにおかしい値が出たらとりあえず排除
        if xPos_pct < -120 or 120 < xPos_pct:
            xPos_pct = Nan

        return xPos_pct

    def match(self, context):
        if context['game']['rule'] is None:
            return None

        applicable_modes = [u'ガチヤグラ', u'ガチホコバトル', 'ガチヤグラ', 'ガチホコバトル']
        if not (context['game']['rule']['name'] in applicable_modes):
            return None

        xPos_pct = self.towerPos(context)

        if xPos_pct != xPos_pct:
            # 値がとれていない
            xPos_pct = context['game']['tower']['pos']

        xPos_pct = int(xPos_pct)

        context['game']['tower']['pos'] = xPos_pct
        context['game']['tower']['min'] = min(
            xPos_pct, context['game']['tower']['min'])
        context['game']['tower']['max'] = max(
            xPos_pct, context['game']['tower']['max'])
        return context['game']['tower']

    def __init__(self):
        self.ui_tower_mask = cv2.imread('masks/ui_tower.png')
        self.ui_tower_mask = self.ui_tower_mask[
            self.tower_line_top:self.tower_line_top + self.tower_line_height, self.tower_left:self.tower_left + self.tower_width]

if __name__ == "__main__":
    target = cv2.imread(sys.argv[1])
#	target = cv2.resize(target, (1280, 720))
    obj = IkaScene_RankedBattle()

    context = {
        'engine': {'frame': target},
        'game': {},
    }

    r = obj.match(context)
    cv2.waitKey()
