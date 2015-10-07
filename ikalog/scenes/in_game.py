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
from ikalog.utils.character_recoginizer import *


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

    def match_go_sign(self, context):
        # ゴーサイン (60秒に1度まで)
        msec = context['engine']['msec']
        if (context['scenes']['in_game']['last_go_sign'] + 60 * 1000) < msec:
            if self.mask_go_sign.match(context['engine']['frame']):
                context['scenes']['in_game']['last_go_sign'] = msec
                callPlugins = context['engine']['service']['callPlugins']
                callPlugins('on_game_go_sign')

        return self.mask_go_sign.match(context['engine']['frame'])

    def match_kills1(self, context):
        img_gray = cv2.cvtColor(
            context['engine']['frame'][:, 502:778],
            cv2.COLOR_BGR2GRAY)
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
            else:
                break

        return len(list)

    def match_kills_loop(self):
        # ToDo: 誰をキルしたか認識してカウントする
        in_trigger = False
        last_kills = 0
        context = (yield in_trigger)
        context['scenes']['in_game']['msec_last_kill'] = - 60 * 1000
        context['scenes']['in_game']['frames_since_last_kill'] = 0

        while True:
            context = (yield in_trigger)
            msec = context['engine']['msec']
            callPlugins = context['engine']['service']['callPlugins']
            # タイマーアイコンが検出された状態で呼ばれる

            # 誰かをキルしたか
            kills = self.match_kills1(context)
            if last_kills < kills:
                delta = kills - last_kills
                context['game']['kills'] = context['game']['kills'] + delta
                callPlugins('on_game_killed')

                context['scenes']['in_game']['msec_last_kill'] = msec
                context['scenes']['in_game']['frames_since_last_kill'] = 0
                last_kills = kills
            else:
                context['scenes']['in_game']['frames_since_last_kill'] = context[
                    'scenes']['in_game'].get('frames_since_last_kill', 0) + 1

            # 3秒以上 or 5 フレーム間は last_kill の値を維持する
            c1 = (context['scenes']['in_game'][
                  'msec_last_kill'] + 3 * 1000) < msec
            c2 = (5 < context['scenes']['in_game']['frames_since_last_kill'])

            if (c1 or c2):
                last_kills = min(last_kills, kills)

    def match_dead(self, context):
        return self.mask_dead.match(context['engine']['frame'])

    def recoginize_and_vote_death_reason(self, context):
        if self.deadly_weapon_recoginizer is None:
            return False

        img_weapon = context['engine']['frame'][218:218 + 51, 452:452 + 410]
        img_weapon_gray = cv2.cvtColor(img_weapon, cv2.COLOR_BGR2GRAY)
        ret, img_weapon_b = cv2.threshold(
            img_weapon_gray, 230, 255, cv2.THRESH_BINARY)

        # (覚) 学習用に保存しておくのはこのデータ
        if 0: # (self.time_last_write + 5000 < context['engine']['msec']):
            filename = os.path.join(
                'training', '_deadly_weapons.%s.png' % time.time())
            cv2.imwrite(filename, img_weapon_b)
            self.time_last_write = context['engine']['msec']

        img_weapon_b_bgr = cv2.cvtColor(img_weapon_b, cv2.COLOR_GRAY2BGR)
        weapon_id = self.deadly_weapon_recoginizer.match( img_weapon_b_bgr)

        # 投票する(あとでまとめて開票)
        data = context['scenes']['in_game']
        data['deadly_weapons'][weapon_id] = \
            data['deadly_weapons'].get(weapon_id, 0) + 1

    def count_death_reason_votes(self, context):
        data = context['scenes']['in_game']
        if len(data['deadly_weapons']) == 0:
            return None

        most_possible_id = None
        most_possible_count = 0
        for weapon_id in data['deadly_weapons'].keys():
            weapon_count = data['deadly_weapons'][weapon_id]
            if most_possible_count < weapon_count:
                most_possible_id = weapon_id
                most_possible_count = weapon_count

        if (most_possible_count == 0) or (most_possible_id is None):
            return None

        context['game']['last_death_reason'] = most_possible_id
        context['game']['death_reasons'][most_possible_id] = \
            context['game']['death_reasons'].get( most_possible_id, 0) + 1

        callPlugins = context['engine']['service']['callPlugins']
        callPlugins('on_game_death_reason_identified')

        return most_possible_id

    def match_death_loop(self):
        in_trigger = False
        context = (yield in_trigger)

        context['scenes']['in_game']['msec_last_death'] = 0

        dead = False

        while True:
            while not dead:
                context = (yield dead)

                dead = self.match_dead(context)

            # 死亡した場合

            msec = context['engine']['msec']
            data = context['scenes']['in_game']

            data['deadly_weapons'] = {}
            data['msec_last_death'] = msec

            context['game']['dead'] = True

            callPlugins = context['engine']['service']['callPlugins']
            callPlugins('on_game_dead')

            # TODO: 自分を殺した相手の情報を解析

            while dead:
                context = (yield dead)

                if self.match_dead(context):
                    self.recoginize_and_vote_death_reason(context)
                    continue

                # 3秒以上 or 5 フレーム間は last_kill の値を維持する
                msec = context['engine']['msec']
                data = context['scenes']['in_game']
                c1 = (data['msec_last_death'] + 3 * 1000) < msec
                if c1:
                    dead = False

            # 死亡状態を抜けた。

            # 死因が判れば特定、イベントを発生させる
            self.count_death_reason_votes(context)

            context['game']['dead'] = False

    def match1(self, context):
        context['engine']['inGame'] = self.matchTimerIcon(context)
        callPlugins = context['engine']['service']['callPlugins']

        if not context['engine']['inGame']:
            return False

            msec = context['engine']['msec']

            context['scenes']['in_game'] = {
                'last_go_sign': msec - 60 * 1000,
                'lastDead': msec - 60 * 1000,
                'lastKill': msec - 60 * 1000,
                'kills': 0,
            }

        return context['engine']['inGame']

    def match_loop(self):
        in_trigger = False

        _match_kills_loop = self.match_kills_loop()
        _match_kills_loop.send(None)

        _match_death_loop = self.match_death_loop()
        _match_death_loop.send(None)

        while True:
            context = (yield in_trigger)

            in_trigger = self.match1(context)
            if in_trigger:
                _match_kills_loop.send(context)
                _match_death_loop.send(context)
                self.match_go_sign(context)

    def match(self, context):
        if not 'in_game' in context['scenes']:
            context['scenes']['in_game'] = {
                'dead': False,
                'last_go_sign': - 60 * 1000,
            }
            context['game']['kills'] = 0
            context['game']['dead'] = False
            context['game']['inGame'] = False

        self._match_loop.send(context)

    def __init__(self, debug=False):
        self._match_loop = self.match_loop()
        self._match_loop.send(None)

        self.mask_timer = IkaMatcher(
            self.timer_left, self.timer_top, self.timer_top, self.timer_height,
            img_file='masks/ingame_timer.png',
            threshold=0.9,
            orig_threshold=0.35,
            bg_method=matcher.MM_BLACK(visibility=(0, 32)),
            fg_method=matcher.MM_WHITE(visibility=(160, 256)),
            label='timer_icon',
            debug=debug,
        )

        self.mask_go_sign = IkaMatcher(
            472, 140, 332, 139,
            img_file='masks/ui_go.png',
            threshold=0.95,
            orig_threshold=0.5,
            label='Go!',
            bg_method=matcher.MM_WHITE(sat=(0, 255), visibility=(0, 210)),
            fg_method=matcher.MM_WHITE(),
            debug=False,
        )

        # mask_killed
        # 例外的に別途スレッショルド済みのグレー2値画像でマッチングする
        # ため fg_method で visibility=(128, 255) を指定
        # 高画質動画なら threshold = 0.90 でいける
        # ビットレートが低いと threshold = 0.80 か
        # ビットレートが低い場合はイベントのチャタリング対策なども必要

        self.mask_killed = IkaMatcher(
            0, 0, 25, 30,
            img_file='masks/ui_killed.png',
            threshold=0.90,
            orig_threshold=0.10,
            bg_method=matcher.MM_WHITE(sat=(0, 255), visibility=(0, 48)),
            fg_method=matcher.MM_WHITE(visibility=(192, 255)),
            label='killed',
            debug=debug,
        )

        self.mask_dead = IkaMatcher(
            1057, 657, 137, 26,
            img_file='masks/ui_dead.png',
            threshold=0.90,
            orig_threshold=0.30,
            bg_method=matcher.MM_WHITE(sat=(0, 255), visibility=(0, 48)),
            fg_method=matcher.MM_WHITE(visibility=(192, 255)),
            label='dead',
            debug=debug,
        )

        try:
            self.deadly_weapon_recoginizer = DeadlyWeaponRecoginizer()
        except:
            self.deadly_weapon_recoginizer = None


if __name__ == "__main__":

    def callPlugins(context):
        pass

    target = cv2.imread(sys.argv[1])

    context = {
        'engine': {
            'msec': 0,
            'frame': target,
            'service': {
                'callPlugins': callPlugins,
            },
        },
        'game': {},
        'scenes': {},
    }

    obj = InGame(debug=True)

    r = obj.match(context)

    print(obj.matchTimerIcon(context))
    print(context['scenes'][obj])
    cv2.waitKey()
