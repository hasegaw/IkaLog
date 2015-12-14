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

from ikalog.scenes.stateful_scene import StatefulScene
from ikalog.utils import *


class ResultGears(StatefulScene):

    def reset(self):
        super(ResultGears, self).reset()

        self._last_event_msec = - 100 * 1000

    def _state_default(self, context):
        if self.is_another_scene_matched(context, 'GameTimerIcon'):
            return False

        frame = context['engine']['frame']

        if frame is None:
            return False

        matched = self.mask_okane_msg.match(frame) and \
            self.mask_level_msg.match(frame) and \
            self.mask_gears_msg.match(frame) and \
            self._analyze(context)

        if matched:
            game = context['game']
            # game['result_cash_pre'] = game['result_cash']
            self._switch_state(self._state_tracking)

        return matched

    def _state_tracking(self, context):
        frame = context['engine']['frame']

        if frame is None:
            return False

        matched = self.mask_okane_msg.match(frame) and \
            self.mask_level_msg.match(frame) and \
            self.mask_gears_msg.match(frame) and \
            self._analyze(context)

        # 画面が続いているならそのまま
        if matched:
            return True

        # 1000ms 以内の非マッチはチャタリングとみなす
        if not matched and self.matched_in(context, 1000):
            return False

        # それ以上マッチングしなかった場合 -> シーンを抜けている
        if not self.matched_in(context, 30 * 1000, attr='_last_event_msec'):
            self.dump(context)
            self._call_plugins('on_result_gears')

        self._last_event_msec = context['engine']['msec']
        self._switch_state(self._state_default)

        return False

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
            # for field in gear.keys():
            #     cv2.imwrite('/tmp/_gear.%d.%s.png' % (n, field), gear[field])

            # マッチした最後のフレームにおけるギアパワーを返す
            # 未開放のギアパワーがこの試合で開放されたときに位置がずれて正しく認識されない場合がある
            gearstr = {}
            for field in gear:
                if field == 'img_name':
                    continue
                elif field.startswith('img_'):
                    if self.gearpower_recoginizer and self.gearpower_recoginizer.trained:
                        try:
                            result, distance = self.gearpower_recoginizer.match(gear[field])
                            gearstr[field.replace('img_','')] = result
                        except:
                            IkaUtils.dprint('Exception occured in gearpower recoginization.')
                            IkaUtils.dprint(traceback.format_exc())
            gear.update(gearstr)
            gears.append(gear)
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
                if field.startswith('img_'):
                    print('  gear %d : %s : %s' % (n, field, '(image)'))
                else:
                    print('  gear %d : %s : %s' %
                      (n, field, gear[field]))

    def _analyze(self, context):
        frame = context['engine']['frame']

        cash = None
        level = None
        exp = None

        img_cash = frame[110:110 + 55, 798:798 + 294]
        img_level = frame[284:284 + 63, 643:643 + 103]
        img_exp = frame[335:335 + 43, 1007:1007 + 180]

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

        data = context['scenes']['result_gears']

        data['img_cash'] = img_cash
        data['img_level'] = img_level
        data['img_exp'] = img_exp
        data['cash'] = cash
        data['level'] = level
        data['gears'] = gears
        data['exp'] = exp
        # TODO: Slash が処理できるようになったら exp を数値化
        return True

    def _init_scene(self, debug=False):
        self.udemae_recoginizer = UdemaeRecoginizer()
        self.number_recoginizer = NumberRecoginizer()
        self.gearpower_recoginizer = GearpowerRecoginizer()
        self.gearpower_recoginizer.load_model_from_file("data/gearpowers.knn.data")
        self.gearpower_recoginizer.knn_train()

        self.mask_okane_msg = IkaMatcher(
            866, 48, 99, 41,
            img_file='masks/result_gears.png',
            threshold=0.90,
            orig_threshold=0.20,
            bg_method=matcher.MM_BLACK(visibility=(0, 64)),
            fg_method=matcher.MM_WHITE(),
            label='result_gaers/okane',
            debug=debug,
        )

        self.mask_level_msg = IkaMatcher(
            869, 213, 91, 41,
            img_file='masks/result_gears.png',
            threshold=0.90,
            orig_threshold=0.20,
            bg_method=matcher.MM_BLACK(),
            fg_method=matcher.MM_COLOR_BY_HUE(
                hue=(40 - 5, 40 + 5), visibility=(200, 255)),
            label='result_gaers/level',
            debug=debug,
        )

        self.mask_gears_msg = IkaMatcher(
            887, 410, 73, 45,
            img_file='masks/result_gears.png',
            threshold=0.90,
            orig_threshold=0.20,
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
    ResultGears.main_func()
