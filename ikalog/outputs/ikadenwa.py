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

from ikalog.utils import *

# IkaLog Output Plugin: Show message on Console
#


class Ikadenwa(object):

    def on_lobby_matched(self, context):
        # ToDo: もし使えるのなら全プレイヤーの情報(ランク、名前のハッシュ的なもの)をイカデンワに送信
        # イカデンワ側でのユーザマッチングに利用してもらう
        pass

    def on_game_start(self, context):
        # ゲーム開始でステージ名、ルール名が表示されたタイミング
        IkaUtils.dprint('%s: Ikadenwa 操作 (全員ミュート)' % self)

    def on_game_team_color(self, context):
        # チームカラーが判明したらイカデンワに報告する

        for n in range(len(context['game']['team_color_hsv'])):
            team = {0: '自分', 1: '相手'}[n]
            hsv = context['game']['team_color_hsv'][n]

            # ±10度でマッチングすれば多分OK
            hue = hsv[0]
            range1 = (max(0, hue - 10), min(180, hue + 10))
            range2 = (min(180, hue - 10 + 180), min(180, hue + 10 + 180))

            l = [range1]
            if range2[0] < 180:
                l.append(range2)

            IkaUtils.dprint('%s: %s カラー %d マッチ範囲 %s' % (self, team, hue, l))
            if n == 0:
                IkaUtils.dprint('%s: Ikadenwa 操作(上記範囲にいる他のプレイヤーをミュート解除' % self)

        # ToDo: イカデンワに色を通知(してミュートを解除してほしい)
        #       色情報は整数値(HSV) の Hue 、整数値で送信する
        #       ±10度ぐらいでおなじ色を持っているプレイヤーとマッチングして
        #       自動的にミュートを解除してもらえると OK

    def on_game_finish(self, context):
        # マッチが終了したと同時に全員ミュート解除
        IkaUtils.dprint('%s: Ikadenwa 操作 (全員ミュート解除)' % self)
