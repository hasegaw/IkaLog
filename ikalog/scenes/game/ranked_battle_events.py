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
from ikalog.scenes.stateful_scene import StatefulScene


class GameRankedBattleEvents(StatefulScene):

    def reset(self):
        super(GameRankedBattleEvents, self).reset()

        self._last_event_msec = - 100 * 1000
        self._last_mask_matched = None
        self._last_mask_triggered_msec = - 100 * 1000

    def find_best_match(self, frame, matchers_list):
        most_possible = (0, None)

        for matcher in matchers_list:
            matched, fg_score, bg_score = matcher.match_score(frame)
            if matched and (most_possible[0] < fg_score):
                most_possible = (fg_score, matcher)

        return most_possible[1]

    def on_game_reset(self, context):
        self._masks_active = {}

    def on_game_start(self, context):
        rule = IkaUtils.rule2text(context['game']['rule'])
        if rule == 'ガチエリア':
            self._masks_active = self._masks_splatzone.copy()
            self._masks_active.update(self._masks_ranked)
        elif rule == 'ガチホコバトル':
            self._masks_active = self._masks_rainmaker.copy()
            self._masks_active.update(self._masks_ranked)
        elif rule == 'ガチヤグラ':
            self._masks_active = self._masks_towercontrol.copy()
            self._masks_active.update(self._masks_ranked)
        else:
            self._masks_active = {}

    def _state_triggered(self, context):
        frame = context['engine']['frame']
        if frame is None:
            return False

        most_possible = self.find_best_match(
            frame, list(self._masks_active.keys()))
        if most_possible is None:
            self._switch_state(self._state_default)

        if most_possible != self._last_mask_matched:
            IkaUtils.dprint('%s: matched %s' % (self, most_possible))
            self._last_mask_matched = most_possible
            # self._switch_state(self._state_pending)
            return True

    def _state_pending(self, context):
        # if self.is_another_scene_matched(context, 'GameTimerIcon'):
        #    return False

        frame = context['engine']['frame']
        if frame is None:
            return False

        most_possible = self.find_best_match(
            frame, list(self._masks_active.keys()))
        if most_possible is None:
            self._switch_state(self._state_default)

        if most_possible != self._last_mask_matched:
            self._last_mask_matched = most_possible
            return True

        # else: # if most_possbile == self._last_mask_matched:
            # go through

        # not self.matched_in(context, 3000, attr='_last_mask_triggered_msec'):

        if 1:
            event = self._masks_active[most_possible]
            IkaUtils.dprint('%s: trigger an event %s' % (self, event))
            self._call_plugins(event)

        self._last_mask_triggered = most_possible
        self._last_mask_triggered_msec = context['engine']['msec']
        self._switch_state(self._state_triggered)

    def _state_default(self, context):
        if 0:
            rule = IkaUtils.rule2text(context['game']['rule'])
            if rule != 'ガチエリア':
                return False

        if 0:
            if self.is_another_scene_matched(context, 'GameTimerIcon'):
                return False

        frame = context['engine']['frame']
        if frame is None:
            return False

        most_possible = self.find_best_match(
            frame, list(self._masks_active.keys()))

        if most_possible is None:
            return False

        # IkaUtils.dprint('%s: matched %s' % (self, most_possible))
        self._last_mask_matched = most_possible
        self._switch_state(self._state_pending)
        return True

    def _analyze(self, context):
        pass

    def _load_splatzone_masks(self, debug=False):
        mask_we_got = IkaMatcher(
            452, 177, 361, 39,
            img_file='masks/ja_splatzone_we_got.png',
            threshold=0.9,
            orig_threshold=0.1,
            label='splatzone/we_got',
            bg_method=matcher.MM_NOT_WHITE(),
            fg_method=matcher.MM_WHITE(),
            debug=debug,
        )

        mask_we_lost = IkaMatcher(
            432, 176, 404, 40,
            img_file='masks/ja_splatzone_we_lost.png',
            threshold=0.9,
            orig_threshold=0.1,
            label='splatzone/we_lost',
            bg_method=matcher.MM_NOT_WHITE(),
            fg_method=matcher.MM_WHITE(),
            debug=debug,
        )

        mask_they_got = IkaMatcher(
            452, 177, 361, 39,
            img_file='masks/ja_splatzone_they_got.png',
            threshold=0.9,
            orig_threshold=0.1,
            label='splatzone/they_got',
            bg_method=matcher.MM_NOT_WHITE(),
            fg_method=matcher.MM_WHITE(),
            debug=debug,
        )

        mask_they_lost = IkaMatcher(
            432, 176, 404, 40,
            img_file='masks/ja_splatzone_they_lost.png',
            threshold=0.9,
            orig_threshold=0.1,
            label='splatzone/they_lost',
            bg_method=matcher.MM_NOT_WHITE(),
            fg_method=matcher.MM_WHITE(),
            debug=debug,
        )

        self._masks_splatzone = {
            mask_we_got:    'on_game_splatzone_we_got',
            mask_we_lost:   'on_game_splatzone_we_lost',
            mask_they_got:  'on_game_splatzone_they_got',
            mask_they_lost: 'on_game_splatzone_they_lost',
        }

    def _load_rainmaker_masks(self, debug=False):
        mask_we_got = IkaMatcher(
            452, 177, 361, 39,
            img_file='masks/ja_rainmaker_we_got.png',
            threshold=0.9,
            orig_threshold=0.1,
            label='rainmaker/we_got',
            bg_method=matcher.MM_NOT_WHITE(),
            fg_method=matcher.MM_WHITE(),
            debug=debug,
        )

        mask_we_lost = IkaMatcher(
            432, 176, 404, 40,
            img_file='masks/ja_rainmaker_we_lost.png',
            threshold=0.9,
            orig_threshold=0.1,
            label='rainmaker/we_lost',
            bg_method=matcher.MM_NOT_WHITE(),
            fg_method=matcher.MM_WHITE(),
            debug=debug,
        )

        mask_they_got = IkaMatcher(
            452, 177, 361, 39,
            img_file='masks/ja_rainmaker_they_got.png',
            threshold=0.9,
            orig_threshold=0.1,
            label='rainmaker/they_got',
            bg_method=matcher.MM_NOT_WHITE(),
            fg_method=matcher.MM_WHITE(),
            debug=debug,
        )

        mask_they_lost = IkaMatcher(
            432, 176, 404, 40,
            img_file='masks/ja_rainmaker_they_lost.png',
            threshold=0.9,
            orig_threshold=0.1,
            label='rainmaker/they_lost',
            bg_method=matcher.MM_NOT_WHITE(),
            fg_method=matcher.MM_WHITE(),
            debug=debug,
        )

        self._masks_rainmaker = {
            mask_we_got:    'on_game_rainmaker_we_got',
            mask_we_lost:   'on_game_rainmaker_we_lost',
            mask_they_got:  'on_game_rainmaker_they_got',
            mask_they_lost: 'on_game_rainmaker_they_lost',
        }

    def _load_towercontrol_masks(self, debug=False):
        mask_we_took = IkaMatcher(
            452, 177, 361, 39,
            img_file='masks/ja_towercontrol_we_took.png',
            threshold=0.9,
            orig_threshold=0.1,
            label='towercontrol/we_took',
            bg_method=matcher.MM_NOT_WHITE(),
            fg_method=matcher.MM_WHITE(),
            debug=debug,
        )

        mask_we_lost = IkaMatcher(
            432, 176, 404, 40,
            img_file='masks/ja_towercontrol_we_lost.png',
            threshold=0.9,
            orig_threshold=0.1,
            label='towercontrol/we_lost',
            bg_method=matcher.MM_NOT_WHITE(),
            fg_method=matcher.MM_WHITE(),
            debug=debug,
        )

        mask_they_took = IkaMatcher(
            452, 177, 361, 39,
            img_file='masks/ja_towercontrol_they_took.png',
            threshold=0.9,
            orig_threshold=0.1,
            label='towercontrol/they_took',
            bg_method=matcher.MM_NOT_WHITE(),
            fg_method=matcher.MM_WHITE(),
            debug=debug,
        )

        mask_they_lost = IkaMatcher(
            432, 176, 404, 40,
            img_file='masks/ja_towercontrol_they_lost.png',
            threshold=0.9,
            orig_threshold=0.1,
            label='towercontrol/they_lost',
            bg_method=matcher.MM_NOT_WHITE(),
            fg_method=matcher.MM_WHITE(),
            debug=debug,
        )

        self._masks_towercontrol = {
            mask_we_took:    'on_game_towercontrol_we_took',
            mask_we_lost:   'on_game_towercontrol_we_lost',
            mask_they_took:  'on_game_towercontrol_they_took',
            mask_they_lost: 'on_game_towercontrol_they_lost',
        }

    def _init_scene(self, debug=False):
        self._masks_active = {}
        self._load_rainmaker_masks(debug=debug)
        self._load_splatzone_masks(debug=debug)
        self._load_towercontrol_masks(debug=debug)

        self.mask_we_lead = IkaMatcher(
            473, 173, 322, 40,
            img_file='masks/ja_ranked_we_lead.png',
            threshold=0.9,
            orig_threshold=0.1,
            label='splatzone/we_lead',
            bg_method=matcher.MM_NOT_WHITE(),
            fg_method=matcher.MM_WHITE(),
            debug=debug,
        )

        self.mask_they_lead = IkaMatcher(
            473, 173, 322, 40,
            img_file='masks/ja_ranked_they_lead.png',
            threshold=0.9,
            orig_threshold=0.1,
            label='splatzone/they_lead',
            bg_method=matcher.MM_NOT_WHITE(),
            fg_method=matcher.MM_WHITE(),
            debug=debug,
        )

        self._masks_ranked = {
            self.mask_we_lead:   'on_game_ranked_we_lead',
            self.mask_they_lead: 'on_game_ranked_they_lead',
        }

if __name__ == "__main__":
    GameRankedBattleEvents.main_func()
