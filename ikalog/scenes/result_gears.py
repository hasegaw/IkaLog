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


class ResultGears(object):

    def match1(self, context):
        frame = context['engine']['frame']

        if not self.mask_okane_msg.match(frame):
            return False

        if not self.mask_level_msg.match(frame):
            return False

        if not self.mask_gears_msg.match(frame):
            return False

        return True

    def analyzeGears(self, context):
        gears = []
        x_list = [613, 613 + 209, 613 + 209 * 2]
        for n in range(3):
            x = x_list[n]
            img_gear = context['engine']['frame'][457:457 + 233, x: x + 204]

            gear = {}
            gear['img_name'] = img_gear[9:9 + 25, 3:3 + 194]
            gear['img_main'] = img_gear[105:105 + 50, 78:78 + 52]
            gear['img_sub1'] = img_gear[158:158 + 36, 41:41 + 37]
            gear['img_sub2'] = img_gear[158:158 + 36, 85:85 + 37]
            gear['img_sub3'] = img_gear[158:158 + 36, 130:130 + 37]
            gears.append(gear)

#            for field in gear.keys():
#                cv2.imwrite('/tmp/_gear.%d.%s.png' % (n, field), gear[field])
        return gears

    def dump(self, context):
        for field in context['scenes']['result_gears']:
            if field == 'gears':
                continue
            elif field.startswith('img_'):
                print('  %s: %s' % (field, '(image)'))
            else:
                print('  %s: %s' %
                      (field, context['scenes']['result_gears'][field]))

        for n in range(len(context['scenes']['result_gears']['gears'])):
            gear = context['scenes']['result_gears']['gears'][n]
            for field in gear:
                print('  gear %d : %s' % (n, field))

    def analyze(self, context):
        cash = None
        level = None
        exp = None
        img_cash = context['engine']['frame'][110:110 + 55, 798:798 + 294]
        img_level = context['engine']['frame'][284:284 + 63, 643:643 + 103]
        img_exp = context['engine']['frame'][335:335 + 43, 1007:1007 + 180]

        try:
            cash = self.number_recoginizer.match_digits(
                img_cash,
                num_digits=(7, 7),
                char_width=(5, 34),
                char_height=(28, 37),
            )
            level = self.number_recoginizer.match_digits(img_level)
            exp = self.number_recoginizer.match(img_exp)  # 整数ではない
        except:
            # FIXME
            pass

        if (cash is None) or (level is None) or (exp is None):
            return False

        gears = self.analyzeGears(context)
        if not ('result_gears' in context['scenes']):
            context['scenes']['result_gears'] = {}

        context['scenes']['result_gears']['img_cash'] = img_cash
        context['scenes']['result_gears']['img_level'] = img_level
        context['scenes']['result_gears']['img_exp'] = img_exp
        context['scenes']['result_gears']['cash'] = cash
        context['scenes']['result_gears']['level'] = level
        context['scenes']['result_gears']['gears'] = gears
        context['scenes']['result_gears']['exp'] = exp
        # TODO: Slash が処理できるようになったら exp を数値化
        return True

    def match_loop(self):

        while True:
            msec_last = 0
            in_trigger = False

            while not in_trigger:
                context = (yield in_trigger)

                if context['engine']['msec'] < (msec_last + 3 * 1000):
                    continue
                in_trigger = self.match1(context)

            # in_trigger = True
            msec_start = context['engine']['msec']
            missed_frames = 0

            # Now entered to the scene.

            # TODO: 左上の数字が白くなくなったら?

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

            # Now escaped from the scene.

            duration = (msec_last - msec_start)
            IkaUtils.dprint('%s: duration = %d ms' % (self, duration))

            if 1:  # if duration > 3 * 1000:
                callPlugins = context['engine']['service']['callPlugins']
                callPlugins('on_result_gears')

    def match(self, context):
        return self.cor.send(context)

    def __init__(self, debug=False):
        self.cor = self.match_loop()
        self.cor.send(None)

        self.udemae_recoginizer = UdemaeRecoginizer()
        self.number_recoginizer = NumberRecoginizer()

        self.mask_okane_msg = IkaMatcher(
            866, 48, 99, 41,
            img_file='masks/result_gears.png',
            threshold=0.7,
            orig_threshold=0.300,
            bg_method=matcher.MM_BLACK(visibility=(0, 64)),
            fg_method=matcher.MM_WHITE(),
            label='result_gaers/okane',
            debug=debug,
        )

        self.mask_level_msg = IkaMatcher(
            869, 213, 91, 41,
            img_file='masks/result_gears.png',
            threshold=0.5,
            orig_threshold=0.300,
            bg_method=matcher.MM_BLACK(),
            fg_method=matcher.MM_COLOR_BY_HUE(
                hue=(40 - 5, 40 + 5), visibility=(200, 255)),
            label='result_gaers/level',
            debug=debug,
        )

        self.mask_gears_msg = IkaMatcher(
            887, 410, 73, 45,
            img_file='masks/result_gears.png',
            threshold=0.7,
            orig_threshold=0.300,
            bg_method=matcher.MM_BLACK(),
            fg_method=matcher.MM_WHITE(),
            label='result_gaers/gears',
            debug=debug,
        )

        try:
            self.number_recoginizer = character_recoginizer.NumberRecoginizer()
        except:
            self.number_recoginizer = None

if __name__ == "__main__":
    target = cv2.imread(sys.argv[1])
    obj = ResultGears(debug=True)

    context = {
        'engine': {'frame': target},
        'game': {},
        'scenes': {},
    }

    matched = obj.match(context)
    analyzed = obj.analyze(context)
    print("matched %s analyzed %s" % (matched, analyzed))
    obj.dump(context)

    cv2.waitKey()
