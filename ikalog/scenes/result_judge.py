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


class ResultJudge(object):

    def match1(self, context):
        frame = context['engine']['frame']

        if frame is None:
            return False

        match_win = self.mask_win.match(frame)
        match_lose = self.mask_lose.match(frame)

        match_win_or_lose = (match_win or match_lose) and (
            not (match_win and match_lose))
        if not match_win_or_lose:
            return False

        img_bar = context['engine']['frame'][600:600 + 30, 126:126 + 1028, :]
        img_bar_hsv = cv2.cvtColor(img_bar, cv2.COLOR_BGR2HSV)
        ret, img_bar_b = cv2.threshold(
            img_bar_hsv[:, :, 2], 96, 255, cv2.THRESH_BINARY)

        img_bar_b_hist = cv2.calcHist([img_bar_b], [0], None, [3], [0, 256])
        raito = img_bar_b_hist[2] / np.sum(img_bar_b_hist)

        if (raito > 0.9):
            context['game']['judge'] = 'win' if match_win else 'lose'

        return True

    def analyze(self, context):
        win_ko = bool(self.mask_win_ko.match(context['engine']['frame']))
        lose_ko = bool(self.mask_lose_ko.match(context['engine']['frame']))

        # win_ko もしくは lose_ko が検出されたらノックアウト。
        # ただし以前のフレームで検出したノックアウトが検出できなくなっている
        # 場合があるので、すでにノックアウト状態であればノックアウトのまま。
        knockout = win_ko or lose_ko or context['game'].get('knockout', False)

        context['game']['knockout'] = knockout

        # 数字がある部分を絞り込む
        x_list = [116, 758]

        white_filter = matcher.MM_WHITE()
        black_filter = matcher.MM_BLACK()
        array0to1280 = np.array(range(1280), dtype=np.int32)
        nawabari_scores_pct = []
        ranked_scores = []
        earned_scores = []

        for team in range(len(x_list)):
            x1 = x_list[team]
            x2 = x1 + 400

            # 2段目(黒色)
            img_num2 = context['engine']['frame'][638:638+32, x1:x2]
            img_num2_b = black_filter.evaluate(img_bgr=img_num2)

            # 2段目が認識できれば
            s = self.number_recoginizer.match_digits(
                cv2.cvtColor(img_num2_b, cv2.COLOR_GRAY2BGR),
                num_digits=(2, 5),
                char_width=(10, 30),
            )

            if s is not None:
                # 最後に p に相当する文字がついているのでそれを落とす
                earned_score = int(int(s) / 10)
                earned_scores.append(earned_score)

            if knockout:
                continue

            # 1段目(白色)
            img_num1 = context['engine']['frame'][567:567 + 70, x1:x2]
            img_num1_b = white_filter.evaluate(img_bgr=img_num1)
            img_num1_b_top = img_num1_b[0:17, :]

            # さらに認識する部分のみに絞り込む
            img_num1_b_top1 = np.sum(img_num1_b_top / 255, axis=0)  # 列毎の検出dot数
            img_num1_extract_x = np.extract(
                img_num1_b_top1 > 0, array0to1280[0:len(img_num1_b_top1)])

            # 1段目が認識できれば
            if len(img_num1_extract_x) > 1:
                x1 = np.amin(img_num1_extract_x)
                x2 = np.amax(img_num1_extract_x) + 1

                if (x2 - x1) < 4:
                    return False

                # ガチマッチ: xxカウント
                try:
                    s = self.number_recoginizer.match_digits(
                        cv2.cvtColor(
                            img_num1_b[:, x1 - 10:x2 + 20], cv2.COLOR_GRAY2BGR),
                        num_digits=(1, 2),
                    )
                except:
                    IkaUtils.dprint('Exception at recoginizing ranked scores')
                    return False

                if s != None:
                    ranked_scores.append(s)
                    continue

                # ナワバリバトル: xx.x%

                try:
                    s = self.number_recoginizer.match_float(
                        cv2.cvtColor(
                            img_num1_b[:, x1 - 10:x2 + 20], cv2.COLOR_GRAY2BGR),
                        num_digits=(1, 4),
                    )
                except:
                    IkaUtils.dprint(
                        'Exception at recoginizing nawabari scores')
                    return

                if s != None:
                    nawabari_scores_pct.append(s)
                    continue

                # cv2.imshow('%d: num' % team, img_num1_b[:, x1:x2])
                # cv2.imshow('%d: top' % team, img_num1_b_top)

        if len(earned_scores) == 2:
            self.last_earned_scores = earned_scores

        if len(nawabari_scores_pct) == 2:
            self.last_nawabari_scores_pct = nawabari_scores_pct
            self.last_ranked_scores = None

        if len(ranked_scores) == 2:
            self.last_nawabari_scores_pct = None
            self.last_ranked_scores = ranked_scores

    def match_loop_func(self):

        msec_last = 0

        while True:
            in_trigger = False

            # シーン外 -> シーンへの突入

            while not in_trigger:
                context = (yield in_trigger)

                if context['engine']['msec'] < (msec_last + 10 * 1000):
                    continue
                in_trigger = self.match1(context)

            # シーン突入した

            msec_start = context['engine']['msec']
            missed_frames = 0

            context['game']['image_judge'] = context['engine']['frame'].copy()

            # シーン中のループ

            while in_trigger:
                context = (yield in_trigger)
                if self.match1(context):
                    msec_last = context['engine']['msec']
                    missed_frames = 0
                    self.analyze(context)
                else:
                    missed_frames = missed_frames + 1
                    if missed_frames > 5:
                        break

            # シーンから抜けた

            duration = (msec_last - msec_start)
            IkaUtils.dprint('%s: duration = %d ms' % (self, duration))

            if 1:  # if duration > 2 * 1000:
                if self.last_earned_scores is not None:
                    context['game'][
                        'earned_scores'] = self.last_earned_scores

                if self.last_nawabari_scores_pct is not None:
                    context['game'][
                        'nawabari_scores_pct'] = self.last_nawabari_scores_pct
                if self.last_ranked_scores is not None:
                    context['game']['ranked_scores'] = self.last_ranked_scores

                callPlugins = context['engine']['service']['callPlugins']
                callPlugins('on_result_judge')

    def match(self, context):
        return self.match_loop.send(context)

    def __init__(self, debug=False):
        self.last_earned_scores = None
        self.last_nawabari_scores_pct = None
        self.last_ranked_scores = None

        self.match_loop = self.match_loop_func()
        self.match_loop.send(None)

        self.number_recoginizer = NumberRecoginizer()

        self.mask_win = IkaMatcher(
            73, 34, 181, 94,
            img_file='masks/result_judge_win.png',
            threshold=0.9,
            orig_threshold=0.100,
            bg_method=matcher.MM_NOT_WHITE(),
            fg_method=matcher.MM_WHITE(),
            label='result_judge/win',
            debug=debug,
        )

        self.mask_win_ko = IkaMatcher(
            123, 572, 318, 57,
            img_file='masks/result_judge_win.png',
            threshold=0.9,
            orig_threshold=0.100,
            bg_method=matcher.MM_NOT_WHITE(),
            fg_method=matcher.MM_WHITE(),
            label='result_judge/win_ko',
            debug=debug,
        )

        self.mask_lose = IkaMatcher(
            73, 34, 181, 94,
            img_file='masks/result_judge_lose.png',
            threshold=0.9,
            orig_threshold=0.100,
            bg_method=matcher.MM_NOT_WHITE(),
            fg_method=matcher.MM_WHITE(),
            label='result_judge/lose',
            debug=debug,
        )

        self.mask_lose_ko = IkaMatcher(
            820, 572, 318, 57,
            img_file='masks/result_judge_lose.png',
            threshold=0.9,
            orig_threshold=0.100,
            bg_method=matcher.MM_NOT_WHITE(),
            fg_method=matcher.MM_WHITE(),
            label='result_judge/lose_ko',
            debug=debug,
        )

        try:
            self.number_recoginizer = character_recoginizer.NumberRecoginizer()
        except:
            self.number_recoginizer = None

if __name__ == "__main__":
    target = cv2.imread(sys.argv[1])
    obj = ResultJudge(debug=True)

    context = {
        'engine': {'frame': target},
        'game': {},
        'scenes': {},
    }

    matched = obj.match1(context)
    analyzed = obj.analyze(context)
    print(matched)
    print(context['game'])
    cv2.waitKey()
