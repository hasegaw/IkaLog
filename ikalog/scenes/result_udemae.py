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


class ResultUdemae(object):

    def match1(self, context):
        frame = context['engine']['frame']
        matched = self.mask_udemae_msg.match(frame)
        return matched

    def analyze(self, context):
        try:
            frame = context['engine']['frame']
            img_udemae = frame[357:357 + 108, 450:450 + 190]
            img_udemae_exp = frame[310:310 + 185, 770:770 + 110]

            udemae_str = None
            udemae_exp = None

            if self.number_recoginizer:
                udemae_exp = self.number_recoginizer.match_digits(
                    img_udemae_exp)
                if udemae_exp < 0 or udemae_exp > 100:
                    udemae_exp = None

            if self.udemae_recoginizer:
                udemae_str = self.udemae_recoginizer.match(img_udemae)
                if not (udemae_str in ['s+', 's', 'a+', 'a', 'a-', 'b+', 'b', 'b-', 'c+', 'c', 'c-']):
                    udemae_str = None
        except:
            return False

        if not (udemae_str and udemae_exp):
            return False

        if not ('result_udemae' in context['scenes']):
            context['scenes']['result_udemae'] = {
                'udemae_str_pre': udemae_str,
                'udemae_exp_pre': udemae_exp,
            }
        context['scenes']['result_udemae']['udemae_str_after'] = udemae_str
        context['scenes']['result_udemae']['udemae_exp_after'] = udemae_exp

        return True

    def match_loop(self):

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
            false_positive_method=IkaMatcher.FP_BACK_IS_BLACK,
            pre_threshold_value=205,
            label='result_udemae/Udemae',
            debug=debug,
        )

        try:
            self.number_recoginizer = character_recoginizer.NumberRecoginizer()
        except:
            self.number_recoginizer = None

        try:
            self.udemae_recoginizer = character_recoginizer.UdemaeRecoginizer()
        except:
            self.udemae_recoginizer = None


if __name__ == "__main__":
    target = cv2.imread(sys.argv[1])
    obj = ResultUdemae(debug=True)

    context = {
        'engine': {'frame': target},
        'game': {},
    }

    matched = obj.match(context)
    analyzed = obj.analyze(context)
    print("matched %s" % (matched))

    cv2.waitKey()
