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

from ikalog.utils import *
import ikalog.utils.matcher as matcher


class ResultUdemae(object):

    valid_udemae_list = [
        's+', 's', 'a+', 'a', 'a-', 'b+', 'b', 'b-', 'c+', 'c', 'c-'
    ]

    def match1(self, context):
        frame = context['engine']['frame']
        matched = self.mask_udemae_msg.match(frame)
        return matched

    def analyze(self, context):
        udemae_str = None
        udemae_exp = None

        frame = context['engine']['frame']
        img_udemae = frame[357:357 + 108, 450:450 + 190]
        img_udemae_exp = frame[310:310 + 185, 770:770 + 110]

        # ウデマエ(文字部分)
        if self.udemae_recoginizer:
            udemae_str = self.udemae_recoginizer.match(img_udemae)

        if not (udemae_str in self.valid_udemae_list):
            udemae_str = None

        # ウデマエ(数値部分)
        if self.number_recoginizer:
            udemae_exp = self.number_recoginizer.match_digits(
                img_udemae_exp)

        if (udemae_exp is not None):
            # ウデマエの数字は 0~100 (99?) しかありえない
            if (udemae_exp < 0) or (udemae_exp > 100):
                udemae_exp = None

        # ウデマエが正しく取得できない場合は別の画面を誤認識している
        # 可能性が高い

        if not (udemae_str and udemae_exp):
            return False

        # 認識開始直後なら udemae_(str|exp)_pre を設定
        # FIXME

        if not ('result_udemae' in context['scenes']):
            context['scenes']['result_udemae'] = {
                'udemae_str_pre': udemae_str,
                'udemae_exp_pre': udemae_exp,
            }

        # udemae_(str|exp)_after は常に最新の値を指す

        context['scenes']['result_udemae']['udemae_str_after'] = udemae_str
        context['scenes']['result_udemae']['udemae_exp_after'] = udemae_exp

        return True

    def match_loop(self):
        # FIXME: チャタリング対策
        # FIXME: 投票ベース検出にする
        in_trigger = False

        while True:
            context = (yield in_trigger)
            callPlugins = context['engine']['service']['callPlugins']
            t = context['engine']['msec']

            if self.match1(context):
                r = self.analyze(context)
                if r:
                    context['scenes']['result_udemae'][
                        'last_update'] = context['engine']['msec']
                    in_trigger = True
                # FIXME: r == False の場合別シーンの誤認識 or チャタリング

            else:
                if in_trigger:
                    last_match = context['scenes'][
                        'result_udemae']['last_update']
                    if ((last_match + 100) < t):
                        # トリガ状態だが未検出状態がしばらく続いた
                        callPlugins('on_result_udemae')
                        in_trigger = False

    def match(self, context):
        return self.cor.send(context)

    def __init__(self, debug=False):
        self.cor = self.match_loop()
        self.cor.send(None)

        # "ウデマエ" 文字列。オレンジ色。 IkaMatcher の拡張が必要
        self.mask_udemae_msg = IkaMatcher(
            561, 245, 144, 52,
            img_file='masks/result_udemae.png',
            threshold=0.5,
            orig_threshold=0.250,
            fg_method=matcher.MM_COLOR_BY_HUE(
                hue=(11 - 5, 11 + 5), visibility=(200, 255)),
            bg_method=matcher.MM_BLACK(visibility=(0, 64)),
            label='result_udemae/Udemae',
            debug=debug,
        )

        self.number_recoginizer = character_recoginizer.NumberRecoginizer()
        self.udemae_recoginizer = character_recoginizer.UdemaeRecoginizer()


if __name__ == "__main__":
    target = cv2.imread(sys.argv[1])
    obj = ResultUdemae(debug=True)

    def callPlugins(event):
        pass

    context = {
        'engine': {
            'msec': 0,
            'frame': target,
            'service': {
                'callPlugins': callPlugins
            },
        },
        'game': {
        },
        'scenes': {
        },
    }

    matched = obj.match(context)
    analyzed = obj.analyze(context)
    print("matched %s" % (matched))

    for field in context['scenes']['result_udemae']:
        if field.startswith('img_'):
            value = '(image)'
    print(context['scenes'])

    cv2.waitKey()
