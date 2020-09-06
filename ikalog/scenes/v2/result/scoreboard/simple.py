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

import copy
import re
import traceback
import time
import os

import numpy as np

import cv2

from PIL import ImageFont, ImageDraw, Image

from ikalog.ml.classifier import ImageClassifier
from ikalog.ml.text_reader import TextReader
from ikalog.scenes.stateful_scene import StatefulScene
from ikalog.inputs.filters import OffsetFilter
from ikalog.utils import *

from ikalog.scenes.v2.result.scoreboard.extract import extract_players
from ikalog.scenes.v2.result.scoreboard.team_colors import extract_team_colors
from ikalog.utils.ikamatcher2.matcher import MultiClassIkaMatcher2 as MultiClassIkaMatcher


scale = 8
font = ImageFont.truetype("Splatoon2.otf", 18 * scale)
class Spl2ResultScoreboard(StatefulScene):

    def _add_player_name_mask(self, name, team=0):
        pil_im = Image.new("RGB", (150*scale, 25*scale), (255, 255, 255))
        draw = ImageDraw.Draw(pil_im)
        draw.text((4.5 * scale, -5.25*scale), name, (0,0,0), font=font, features=["kern"])
        pil_im.thumbnail((150,25))
        player_name_im = cv2.cvtColor(np.array(pil_im), cv2.COLOR_RGB2BGR)

        mask = IkaMatcher(
            0, 0, 150, 25,
            img=player_name_im,
            threshold= 0.9,
            orig_threshold= 0.02,
            bg_method=matcher.MM_BLACK(visibility=(0, 215)),
            fg_method=matcher.MM_WHITE(visibility=(150,255)),
            label=name,
            call_plugins=self._call_plugins,
            debug=False
        )

        if team == 1:
            self._player_masks_team1.add_mask(mask)
        else:
            self._player_masks_team0.add_mask(mask)



    def _read_int(self, img):
        #cv2.imshow('read char', img)

        img = cv2.resize(img, (img.shape[1] * 3, img.shape[0] * 3))

        img_hsv = cv2.cvtColor(img, cv2.COLOR_BGR2HSV)
        img_gray = img_hsv[:, :, 2]
        img_gray[img_gray < 200] = 0
        img_gray[img_hsv[:, :, 1] > 30] = 0
        img_gray[img_gray > 0] = 255

        val_str, val_int = None, None
        img_bgr = cv2.cvtColor(img_gray, cv2.COLOR_GRAY2BGR)
        return self._tr.read_int(img_gray)
        if 1:
            val_str = self._tr.read_char(img_gray)
            print('Read: %s' % val_str)

        try:
            val_int = int(val_str)
        except:
            pass

        #cv2.imshow('%s' % val_str, img_bgr)
        # cv2.waitKey(1000)
        return val_int

    def _matches_name(self, img, team=0, label=''):
        if team == 1:
            (bg, fg, mask) = self._player_masks_team1.match_best_bg_fg(img, label=label)
        else:
            (bg, fg, mask) = self._player_masks_team0.match_best_bg_fg(img, label=label)
        if mask:
            return mask._label
        return None

    def analyze(self, context):
        context['game']['players'] = []
        weapon_list = []

        return

    def reset(self):
        super(Spl2ResultScoreboard, self).reset()

        self._last_event_msec = - 100 * 1000
        self._match_start_msec = - 100 * 1000

        self._last_frame = None
        self._diff_pixels = []

        self._player_masks_team0 = MultiClassIkaMatcher()
        self._player_masks_team1 = MultiClassIkaMatcher()

    def check_match(self, context):
        frame = context['engine']['frame']

        if frame is None:
            return False

        img = self._c_win.extract_rect(context['engine']['frame'])
        img_v = np.array(cv2.cvtColor(img, cv2.COLOR_BGR2HSV)
                         [:, :, 2], dtype=np.float32)

        # min-max
        img_v_2 = img_v - np.min(img_v)
        img_v_3 = img_v_2 / np.maximum(1, np.max(img_v_2)) * 255
        img_v_4 = np.array(img_v_3, dtype=np.uint8)
        img_a = cv2.cvtColor(img_v_4, cv2.COLOR_GRAY2BGR)

        # cv2.imshow('result', img_a)

        matched = self._c_win.predict1(img_a) >= 0
        return matched

    def _state_default(self, context):
        # pass matching in some scenes.
        session = self.find_scene_object('V2GameSession')
        if session is not None:
            if not (session._state.__name__ in ('_state_default', '_state_battle_finish')):
                return False

        frame = context['engine']['frame']
        if frame is None:
            return False

        if self.matched_in(context, 30 * 1000):
            return False

        matched = self.check_match(context)
        if matched:
            self._switch_state(self._state_tracking)

            context['game']['image_scoreboard'] = \
                copy.deepcopy(context['engine']['frame'])
            self._call_plugins_later('on_result_detail_still')

            self._call_plugins('get_player_names')
            players = extract_players(frame)

            if self._engine and self._engine.context['game']['player_names']:
                for index, name in enumerate(self._engine.context['game']['player_names']):
                    team = 1 if index < 4 else 0
                    if context['game']['won']:
                        team = 0 if index < 4 else 1
                    if name:
                        self._add_player_name_mask(name, team)


            for index, p in enumerate(players):
                try:
                    score = self._tr.read_char(p['img_score'])
                    p['score'] = re.sub(r'p$', r'', score)
                except:
                    # FIXME
                    pass

                p['kill_or_assist'] = self._read_int(p['img_kill_or_assist'])
                p['special'] = self._read_int(p['img_special'])
                
                cv2.imwrite('player-%s.png' % index, p['img_name'])
                p['name'] = self._matches_name(p['img_name'], 0 if index < 4 else 1, index)

                # backward compatibility
                p['me'] = p.get('myself')

            context['game']['players'] = players

            # won?
            # TODO - need to cater to spectator alpha/bravo perspective
            if 'won' not in context['game'] or context['game']['won'] == None:
                me_matches = list(filter(lambda x: x['myself'], players))
                me = me_matches[0] if len(me_matches) else {'team': 0}
                context['game']['won'] = (me['team'] == 0)

            # team colors
            team_colors = \
                extract_team_colors(context, context['engine']['frame'])
            context['game']['my_team_color'] = team_colors[0]
            context['game']['counter_team_color'] = team_colors[1]

            # for debug....
            context['game']['lobby'] = 'private'

            self.dump(context)

            self._call_plugins_later('on_result_detail')
            self._call_plugins_later('on_game_individual_result')

#        if matched:
#            self._match_start_msec = context['engine']['msec']
#            self._switch_state(self._state_tracking)
        return matched

    def _state_tracking(self, context):
        frame = context['engine']['frame']

        matched = self.check_match(context)
        escaped = not self.matched_in(context, 1000)

        if escaped:
            self._switch_state(self._state_default)

        return matched

    def dump(self, context):
        print('--------')
        print('won: ', context['game']['won'])

        for e in context['game']['players']:
            kill = e.get('kill')
            ka = e.get('kill_or_assist')
            special = e.get('special')
            score = e.get('score')
            name = e.get('name')
            myself = '*' if e.get('myself') else None
            print(name, kill, ka, special, score, myself)

    def _init_scene(self, debug=False):
        self._tr = TextReader()

        self._c_win = ImageClassifier()
        self._c_win.load_from_file('data/spl2/spl2.result.scoreboard_1.dat')


if __name__ == "__main__":
    Spl2ResultScoreboard.main_func()
