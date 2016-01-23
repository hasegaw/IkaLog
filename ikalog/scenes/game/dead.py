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
import threading
import traceback

import cv2

from ikalog.api import APIClient
from ikalog.scenes.stateful_scene import StatefulScene
from ikalog.utils import *
from ikalog.utils.character_recoginizer import *


class GameDead(StatefulScene):
    choordinates = {
        'ja': {'top': 218, 'left': 452},
        'en': {'top': 263, 'left': 432},
    }

    def recoginize_and_vote_death_reason(self, context):
        lang_short = Localization.get_game_languages()[0][0:2]

        try:
            c = self.choordinates[lang_short]
        except KeyError:
            c = self.choordinates['en']

        img_weapon = context['engine']['frame'][
            c['top']:c['top'] + 51,
            c['left']:c['left'] + 410
        ]

        img_weapon_gray = cv2.cvtColor(img_weapon, cv2.COLOR_BGR2GRAY)
        img_weapon_hsv = cv2.cvtColor(img_weapon, cv2.COLOR_BGR2HSV)

        img_weapon_gray[img_weapon_hsv[:, :, 1] > 32] = 0
        ret, img_weapon_b = cv2.threshold(
            img_weapon_gray, 220, 255, cv2.THRESH_BINARY)

        # (覚) 学習用に保存しておくのはこのデータ。 Change to 1 for training.
        if 0:  # (self.time_last_write + 5000 < context['engine']['msec']):
            import time
            filename = os.path.join(  # training/ directory must already exist
                'training', '_deadly_weapons.%s.png' % time.time())
            cv2.imwrite(filename, img_weapon_b)
            self.time_last_write = context['engine']['msec']

        # Workaround for languages that deadly_weapons is not trained
        if not Localization.get_game_languages()[0] in ['ja', 'en_NA']:
            return

        img_weapon_b_bgr = cv2.cvtColor(img_weapon_b, cv2.COLOR_GRAY2BGR)
        self.deadly_weapon_images.append(img_weapon_b_bgr)

    def recognize_cause_of_death(self, context):
        deadly_weapon_images = self.deadly_weapon_images
        self.deadly_weapon_images = []
        IkaUtils.dprint('%s: deadly_weapon recognition started.' % self)
        try:
            response = self._client.recoginize_deadly_weapons(
                deadly_weapon_images)
            if response['status'] == 'ok':
                weapon_id = response['deadly_weapon']
                context['game']['last_death_reason'] = weapon_id
                context['game']['death_reasons'][weapon_id] = \
                    context['game']['death_reasons'].get(weapon_id, 0) + 1

                self._call_plugins_later('on_game_death_reason_identified')
            else:
                IkaUtils.dprint('%s: Server returned an error.' % self)

        except:
            IkaUtils.dprint(
                '%s: Exception occured in deadly_weapon recognition.' % self)
            IkaUtils.dprint(traceback.format_exc())

        IkaUtils.dprint('%s: deadly_weapon recognition finished.' % self)

    def reset(self):
        super(GameDead, self).reset()

        self.deadly_weapon_images = []
        self._last_event_msec = - 100 * 1000
        self._cause_of_death_votes = {}

    def _state_default(self, context):
        if not self.is_another_scene_matched(context, 'GameTimerIcon'):
            return False

        frame = context['engine']['frame']

        if frame is None:
            return False

        matched = self.mask_dead.match(context['engine']['frame'])

        if matched:
            context['game']['dead'] = True
            self._call_plugins('on_game_dead')
            self.recoginize_and_vote_death_reason(context)
            self._switch_state(self._state_tracking)

        return matched

    def _state_tracking(self, context):
        frame = context['engine']['frame']

        if frame is None:
            return False

        matched = self.mask_dead.match(context['engine']['frame'])

        # 画面が続いているならそのまま
        if matched:
            self.recoginize_and_vote_death_reason(context)
            return True

        # 1000ms 以内の非マッチはチャタリングとみなす
        if not matched and self.matched_in(context, 1000):
            return False

        # それ以上マッチングしなかった場合 -> シーンを抜けている
        if not self.matched_in(context, 5 * 1000, attr='_last_event_msec'):
            self.recognize_cause_of_death(context)

            self._call_plugins('on_game_respawn')

        self._last_event_msec = context['engine']['msec']
        self._switch_state(self._state_default)
        context['game']['dead'] = False
        self._cause_of_death_votes = {}
        self.deadly_weapon_images = []

        return False

    def dump(self, context):
        print('last_death_reason %s' % context['game']['death_reasons'])

    def _analyze(self, context):
        pass

    def _init_scene(self, debug=False):
        self.mask_dead = IkaMatcher(
            1057, 657, 137, 26,
            img_file='game_dead.png',
            threshold=0.90,
            orig_threshold=0.30,
            bg_method=matcher.MM_WHITE(sat=(0, 255), visibility=(0, 48)),
            fg_method=matcher.MM_WHITE(visibility=(192, 255)),
            label='dead',
            debug=debug,
        )

        self._client = APIClient(local_mode=True)
        # self._client = APIClient(local_mode=False, base_uri='http://localhost:8000')

if __name__ == "__main__":
    GameDead.main_func()
