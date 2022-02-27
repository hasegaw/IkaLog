#!/usr/bin/env python3
# -*- coding: utf-8 -*-
#
#  IkaLog
#  ======
#  Copyright (C) 2017 Takeshi HASEGAWA
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
from ikalog.ml.classifier import ImageClassifier
from ikalog.utils import *
from ikalog.utils.character_recoginizer import *


class Spl2GameDead(StatefulScene):
    choordinates = {
        'ja': {'top': 238, 'left': 485, 'width': 309, 'height': 31},
        'en': {'top': 263, 'left': 432},
    }

    def recoginize_and_vote_death_reason(self, context):
        lang_short = Localization.get_game_languages()[0][0:2]

        try:
            c = self.choordinates[lang_short]
        except KeyError:
            c = self.choordinates['en']

        if 0:
            cv2.rectangle(context['engine']['preview'],
                pt1=(c['left'], c['top']),
                pt2=(c['left'] + c['width'], c['top'] + c['height']),
                color=(0, 0, 255),
                thickness=2,
                lineType=cv2.LINE_4,
                shift=0)

        img_weapon = context['engine']['frame'][
            c['top']:c['top'] + c['height'],
            c['left']:c['left'] +c['width']
        ]

        if 0:
            cv2.imshow("img_weapon", img_weapon)
            cv2.waitKey(1)

        img_weapon_gray = cv2.cvtColor(img_weapon, cv2.COLOR_BGR2GRAY)
        img_weapon_hsv = cv2.cvtColor(img_weapon, cv2.COLOR_BGR2HSV)

        img_weapon_gray[img_weapon_hsv[:, :, 1] > 32] = 0
        ret, img_weapon_b = cv2.threshold(
            img_weapon_gray, 220, 255, cv2.THRESH_BINARY)

        white_pixels = int(np.sum(img_weapon_b) / 255)
        if z < white_pixels:
            return

        # (覚) 学習用に保存しておくのはこのデータ。 Change to 1 for training.
        if 1:  # (self.time_last_write + 5000 < context['engine']['msec']):
            import time
            filename = os.path.join(  # training/ directory must already exist
                'training', '_deadly_weapons.%s.png' % time.time())
            cv2.imwrite(filename, img_weapon_b)
            self.time_last_write = context['engine']['msec']

        # Workaround for languages that deadly_weapons is not trained
        if not Localization.get_game_languages()[0] in ['ja', 'en_NA']:
            return

        if self.deadly_weapon_recoginizer is None:
            return False

        img_weapon_b_bgr = cv2.cvtColor(img_weapon_b, cv2.COLOR_GRAY2BGR)
        weapon_id = self.deadly_weapon_recoginizer.match(img_weapon_b_bgr)

        if 0:
            cv2.rectangle(context['engine']['preview'],
                pt1=(c['left'], c['top']),
                pt2=(c['left'] + c['width'], c['top'] + c['height']),
                color=(0, 255, 0),
                thickness=2,
                lineType=cv2.LINE_4,
                shift=0)


        if weapon_id == 'unknown':
            return

        # 投票する(あとでまとめて開票)
        votes = self._cause_of_death_votes
        votes[weapon_id] = votes.get(weapon_id, 0) + 1

    def count_death_reason_votes(self, context):
        votes = self._cause_of_death_votes
        if len(votes) == 0:
            return None

        key_list = list(map(lambda key: key, votes.keys()))
        count_list = list(map(lambda key: votes[key], key_list))

        max_index = np.argmax(count_list)
        key = key_list[max_index]

        # softmax
        sum_votes_exp = np.sum(np.exp(count_list))
        accuracy = np.exp(count_list[max_index]) / sum_votes_exp

        print('votes=%s accuracy=%3.3f' % (votes, accuracy))

        context['game']['last_death_reason'] = key
        context['game']['death_reasons'][key] = \
            context['game']['death_reasons'].get(key, 0) + 1

        return key

    def reset(self):
        super(Spl2GameDead, self).reset()

        self._last_event_msec = - 100 * 1000
        self._cause_of_death_votes = {}

    def _state_default(self, context):
        # pass matching in some scenes.
        session = self.find_scene_object('Spl2GameSession')
        if session is not None:
            if not (session._state.__name__ in ('_state_battle')):
                return False

        frame = context['engine']['frame']

        if frame is None:
            return False

        # if not matched and self.matched_in(context, 1000):
        #    return False

        # matched = self._c.predict_frame(context['engine']['frame']) >= 0
        matched = self.mask_dead.match(context['engine']['frame'])

        if matched:
            context['game']['dead'] = True
            self._call_plugins('on_game_dead')
            self.recoginize_and_vote_death_reason(context)
            self._switch_state(self._state_tracking)

            context['game']['death'] = context['game'].get('death', 0) + 1

        return matched

    def _state_tracking(self, context):
        frame = context['engine']['frame']

        if frame is None:
            return False

        # matched = self._c.predict_frame(context['engine']['frame']) >= 0
        matched = self.mask_dead.match(context['engine']['frame'])


        cv2.putText(context['engine']['preview'], text='dead/%s' % matched, org=(1000,600), fontFace=cv2.FONT_HERSHEY_SIMPLEX, fontScale=1.0, color=(0,255,0), thickness=2, lineType=cv2.LINE_4)

        if matched:
            self.recoginize_and_vote_death_reason(context)


        # 画面が続いているならそのまま
        if matched:
            # if not self.is_another_scene_matched(context, 'Spl2InGame'):
            return True

        # 1000ms 以内の非マッチはチャタリングとみなす
        if not matched and self.matched_in(context, 1000):
            return False

        # それ以上マッチングしなかった場合 -> シーンを抜けている
        if not self.matched_in(context, 5 * 1000, attr='_last_event_msec'):
            self.count_death_reason_votes(context)

            if 'last_death_reason' in context['game']:
                self._call_plugins('on_game_death_reason_identified')

            self._call_plugins('on_game_respawn')

        self._last_event_msec = context['engine']['msec']
        self._switch_state(self._state_default)
        context['game']['dead'] = False
        self._cause_of_death_votes = {}

        return False

    def dump(self, context):
        print('last_death_reason %s' % context['game']['death_reasons'])

    def _analyze(self, context):
        pass

    def _init_scene(self, debug=False):
        self.mask_dead = IkaMatcher(
            1092, 648, 96, 26,
            img_file='v2_game_dead.png',
            threshold=0.80,
            orig_threshold=0.40,
            bg_method=matcher.MM_WHITE(sat=(0, 255), visibility=(0, 48)),
            fg_method=matcher.MM_WHITE(visibility=(192, 255)),
            label='dead',
            call_plugins=self._call_plugins,
            debug=debug,
        )

        self._c = ImageClassifier()
        self._c.load_from_file('data/spl2/spl2.game_dead.dat')

        try:
            self.deadly_weapon_recoginizer = DeadlyWeaponRecoginizer()
        except:
            self.deadly_weapon_recoginizer = None


if __name__ == "__main__":
    Spl2GameDead.main_func()
