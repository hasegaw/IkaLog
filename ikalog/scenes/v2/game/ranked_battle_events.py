#!/usr/bin/env python3
# -*- coding: utf-8 -*-
#
#  IkaLog
#  ======
#  Copyright (C) 2018 Takeshi HASEGAWA
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
from ikalog.utils.ikamatcher2.matcher import MultiClassIkaMatcher2 as MultiClassIkaMatcher


class Spl2GameRankedBattleEvents(StatefulScene):

    # Called per Engine's reset.
    def reset(self):
        super(Spl2GameRankedBattleEvents, self).reset()

        self._last_event_msec = - 100 * 1000
        self._last_mask_matched = None
        self._last_mask_triggered_msec = - 100 * 1000
        self._masks_active = {}
        self._masks_active2 = MultiClassIkaMatcher()

    def on_game_reset(self, context):
        self._masks_active = {}
        self._masks_active2 = MultiClassIkaMatcher()

    def on_game_start(self, context):
        rule_id = context['game']['rule']
        masks_active = self._masks_ranked.copy()
        if rule_id == 'area':
            masks_active.update(self._masks_splatzone)

        elif rule_id == 'hoko':
            masks_active.update(self._masks_rainmaker)

        elif rule_id == 'yagura':
            masks_active.update(self._masks_towercontrol)

        elif rule_id == 'asari':
            masks_active.update(self._masks_cramblitz)

        else:
            masks_active = {}

        self._masks_active = masks_active

        # Initialize Multi-Class IkaMatcher
        self._masks_active2 = MultiClassIkaMatcher()
        for mask in masks_active.keys():
            self._masks_active2.add_mask(mask)

    def _state_triggered(self, context):
        frame = context['engine']['frame']
        if frame is None:
            return False

        most_possible = self._masks_active2.match_best(frame)[1]
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

        most_possible = self._masks_active2.match_best(frame)[1]

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
        # if self.is_another_scene_matched(context, 'GameTimerIcon'):
        #     return False

        frame = context['engine']['frame']
        if frame is None:
            return False

        most_possible = self._masks_active2.match_best(frame)[1]

        if most_possible is None:
            return False

        # IkaUtils.dprint('%s: matched %s' % (self, most_possible))
        self._last_mask_matched = most_possible
        self._switch_state(self._state_pending)
        return True

    def _analyze(self, context):
        pass

    def _load_cramblitz_masks(self, debug=False):
        mask_we_broke = IkaMatcher(
            448, 184, 384, 48,
            img_file='v2_cramblitz_we_broke.png',
            threshold=0.9,
            orig_threshold=0.1,
            label='cramblitz/we_broke',
            bg_method=matcher.MM_NOT_WHITE(),
            fg_method=matcher.MM_WHITE(),
            call_plugins=self._call_plugins,
            debug=debug,
        )

        mask_we_back = IkaMatcher(
            448, 184, 384, 48,
            img_file='v2_cramblitz_we_back.png',
            threshold=0.9,
            orig_threshold=0.1,
            label='cramblitz/we_back',
            bg_method=matcher.MM_NOT_WHITE(),
            fg_method=matcher.MM_WHITE(),
            call_plugins=self._call_plugins,
            debug=debug,
        )

        mask_they_broke = IkaMatcher(
            448, 184, 384, 48,
            img_file='v2_cramblitz_they_broke.png',
            threshold=0.9,
            orig_threshold=0.1,
            label='cramblitz/they_broke',
            bg_method=matcher.MM_NOT_WHITE(),
            fg_method=matcher.MM_WHITE(),
            call_plugins=self._call_plugins,
            debug=debug,
        )

        mask_they_back = IkaMatcher(
            448, 184, 384, 48,
            img_file='v2_cramblitz_they_back.png',
            threshold=0.9,
            orig_threshold=0.1,
            label='cramblitz/they_back',
            bg_method=matcher.MM_NOT_WHITE(),
            fg_method=matcher.MM_WHITE(),
            call_plugins=self._call_plugins,
            debug=debug,
        )

        self._masks_cramblitz = {
            mask_we_broke:    'on_game_cramblitz_we_broke',
            mask_we_back:   'on_game_cramblitz_we_back',
            mask_they_broke:  'on_game_cramblitz_they_broke',
            mask_they_back: 'on_game_cramblitz_they_back',
        }

    def _load_splatzone_masks(self, debug=False):
        mask_we_got = IkaMatcher(
            448, 184, 384, 48,
            img_file='v2_splatzone_we_got.png',
            threshold=0.9,
            orig_threshold=0.1,
            label='splatzone/we_got',
            bg_method=matcher.MM_NOT_WHITE(),
            fg_method=matcher.MM_WHITE(),
            call_plugins=self._call_plugins,
            debug=debug,
        )

        mask_we_lost = IkaMatcher(
            448, 184, 384, 48,
            img_file='v2_splatzone_we_lost.png', # same!
            threshold=0.9,
            orig_threshold=0.1,
            label='splatzone/we_lost',
            bg_method=matcher.MM_NOT_WHITE(),
            fg_method=matcher.MM_WHITE(),
            call_plugins=self._call_plugins,
            debug=debug,
        )

        mask_they_got = IkaMatcher(
            448, 184, 384, 48,
            img_file='v2_splatzone_they_got.png',
            threshold=0.9,
            orig_threshold=0.1,
            label='splatzone/they_got',
            bg_method=matcher.MM_NOT_WHITE(),
            fg_method=matcher.MM_WHITE(),
            call_plugins=self._call_plugins,
            debug=debug,
        )

        mask_they_lost = IkaMatcher(
            448, 184, 384, 48,
            img_file='v2_splatzone_they_lost.png', # same!
            threshold=0.9,
            orig_threshold=0.1,
            label='splatzone/they_lost',
            bg_method=matcher.MM_NOT_WHITE(),
            fg_method=matcher.MM_WHITE(),
            call_plugins=self._call_plugins,
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
            448, 184, 384, 48,
            img_file='v2_rainmaker_we_got.png',
            threshold=0.9,
            orig_threshold=0.1,
            label='rainmaker/we_got',
            bg_method=matcher.MM_NOT_WHITE(),
            fg_method=matcher.MM_WHITE(),
            call_plugins=self._call_plugins,
            debug=debug,
        )

        mask_we_lost = IkaMatcher(
            448, 184, 384, 48,
            img_file='v2_rainmaker_we_lost.png',
            threshold=0.9,
            orig_threshold=0.1,
            label='rainmaker/we_lost',
            bg_method=matcher.MM_NOT_WHITE(),
            fg_method=matcher.MM_WHITE(),
            call_plugins=self._call_plugins,
            debug=debug,
        )

        mask_they_got = IkaMatcher(
            448, 184, 384, 48,
            img_file='v2_rainmaker_they_got.png',
            threshold=0.9,
            orig_threshold=0.1,
            label='rainmaker/they_got',
            bg_method=matcher.MM_NOT_WHITE(),
            fg_method=matcher.MM_WHITE(),
            call_plugins=self._call_plugins,
            debug=debug,
        )

        mask_they_lost = IkaMatcher(
            448, 184, 384, 48,
            img_file='v2_rainmaker_they_lost.png',
            threshold=0.9,
            orig_threshold=0.1,
            label='rainmaker/they_lost',
            bg_method=matcher.MM_NOT_WHITE(),
            fg_method=matcher.MM_WHITE(),
            call_plugins=self._call_plugins,
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
            448, 184, 384, 48,
            img_file='v2_towercontrol_we_took.png',
            threshold=0.9,
            orig_threshold=0.1,
            label='towercontrol/we_took',
            bg_method=matcher.MM_NOT_WHITE(),
            fg_method=matcher.MM_WHITE(),
            call_plugins=self._call_plugins,
            debug=debug,
        )

        mask_we_lost = IkaMatcher(
            448, 184, 384, 48,
            img_file='v2_towercontrol_we_lost.png',
            threshold=0.9,
            orig_threshold=0.1,
            label='towercontrol/we_lost',
            bg_method=matcher.MM_NOT_WHITE(),
            fg_method=matcher.MM_WHITE(),
            call_plugins=self._call_plugins,
            debug=debug,
        )

        mask_they_took = IkaMatcher(
            448, 184, 384, 48,
            img_file='v2_towercontrol_they_took.png',
            threshold=0.9,
            orig_threshold=0.1,
            label='towercontrol/they_took',
            bg_method=matcher.MM_NOT_WHITE(),
            fg_method=matcher.MM_WHITE(),
            call_plugins=self._call_plugins,
            debug=debug,
        )

        mask_they_lost = IkaMatcher(
            448, 184, 384, 48,
            img_file='v2_towercontrol_they_lost.png',
            threshold=0.9,
            orig_threshold=0.1,
            label='towercontrol/they_lost',
            bg_method=matcher.MM_NOT_WHITE(),
            fg_method=matcher.MM_WHITE(),
            call_plugins=self._call_plugins,
            debug=debug,
        )

        self._masks_towercontrol = {
            mask_we_took:    'on_game_towercontrol_we_took',
            mask_we_lost:   'on_game_towercontrol_we_lost',
            mask_they_took:  'on_game_towercontrol_they_took',
            mask_they_lost: 'on_game_towercontrol_they_lost',
        }

    # Called only once on initialization.
    def _init_scene(self, debug=False):
        self._load_cramblitz_masks(debug=debug)
        self._load_rainmaker_masks(debug=debug)
        self._load_splatzone_masks(debug=debug)
        self._load_towercontrol_masks(debug=debug)

        self.mask_we_lead = IkaMatcher(
            448, 184, 384, 48,
            img_file='v2_ranked_we_lead.png',
            threshold=0.9,
            orig_threshold=0.1,
            label='splatzone/we_lead',
            bg_method=matcher.MM_NOT_WHITE(),
            fg_method=matcher.MM_WHITE(),
            call_plugins=self._call_plugins,
            debug=debug,
        )

        self.mask_they_lead = IkaMatcher(
            448, 184, 384, 48,
            img_file='v2_ranked_they_lead.png',
            threshold=0.9,
            orig_threshold=0.1,
            label='splatzone/they_lead',
            bg_method=matcher.MM_NOT_WHITE(),
            fg_method=matcher.MM_WHITE(),
            call_plugins=self._call_plugins,
            debug=debug,
        )

        self._masks_ranked = {
            self.mask_we_lead:   'on_game_ranked_we_lead',
            self.mask_they_lead: 'on_game_ranked_they_lead',
        }

if __name__ == "__main__":
    Spl2GameRankedBattleEvents.main_func()
