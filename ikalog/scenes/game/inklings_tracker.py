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

from ikalog.scenes.stateful_scene import StatefulScene
from ikalog.utils import *


class InklingsTracker(StatefulScene):

    meter_center = 640
    meter_width_half = 210
    meter_x1 = meter_center - meter_width_half
    meter_x2 = meter_center + meter_width_half

    def reset(self):
        super(InklingsTracker, self).reset()

    ##
    # _get_vs_xpos(self, context)
    #
    # Find the "vs" character betweeen our team's inklinks and the other's.
    #
    # Returns x_pos value (offset from self.meter_x1), if succeeded ins
    # detecteding the position.
    # Otherwise False. Detection may fail in some scenes
    # (e.g. at the beginning of the game, and low-quality input)
    #
    def _get_vs_xpos(self, context):
        frame = context['engine']['frame']

        img = frame[24 + 38: 24 + 40, self.meter_x1: self.meter_x2]
        img_w = matcher.MM_WHITE(
            sat=(0, 8), visibility=(248, 256))(img)

        img_vs_hist = np.sum(img_w, axis=0)
        img_vs_x = np.extract(img_vs_hist > 128, np.arange(1024))

        if len(img_vs_x) == 0:
            return None

        vs_x_min = np.amin(img_vs_x)
        vs_x_max = np.amax(img_vs_x)
        vs_x = int((vs_x_min + vs_x_max) / 2)
        return vs_x

    ##
    # _find_active_inklings
    #
    # Find active inklings on the frame.
    # @param self    The object.
    # @param context The context.
    # @param x1      Absolute x value to start discovery.
    # @param x2      Absolute x value to finish discovery.
    #
    # This function looks for eye of the inklings (with white pixels).
    #
    # To reduce false-positive detection, it also checks the pixel
    # of the squid. Since it's body should be colored (not white or black),
    # it ignores eye pixels without colored body pixels.
    #
    # team
    def _find_inklings(self, context, x1, x2, team=[False, False, False, False]):
        if (context['engine']['frame'] is None) or not (x1 < x2):
            return team

        frame = context['engine']['frame']
        team = team.copy()

        # Manipulate histgram array of inkling eyes.
        img_eye = matcher.MM_WHITE()(
            frame[24 + 16: 24 + 30, self.meter_x1: self.meter_x2]
        )
        img_eye_hist = np.sum(img_eye, axis=0)

        # Manipulate histgram array of inkling bodies.
        img_fg_b = matcher.MM_WHITE(sat=(40, 255), visibility=(60, 255))(
            frame[24 + 31: 24 + 36, self.meter_x1:self.meter_x2]
        )
        img_fg_hist = np.sum(img_fg_b / 255, axis=0)

        # Mask false-positive values in img_eye_hist.
        img_eye_hist[img_fg_hist < 4] = 0

        if 0:
            cv2.line(frame, (self.meter_x1 + x1, 0),
                     (self.meter_x1 + x1, 50), (0, 0, 0), 2)
            cv2.line(frame, (self.meter_x1 + x2, 0),
                     (self.meter_x1 + x2, 50), (0, 0, 0), 2)

        # Search the inkling bodies.
        x = x1
        direction = 3
        while x < x2:
            x = x + direction

            x_base = x
            add_sample = False
            # Forward until inkling's eyes found.
            while True:
                if not (x < x2):
                    break

                on_eye = img_eye_hist[x] > 128
                if on_eye:
                    # Found.
                    add_sample = True
                    break

                x_base = x
                x = x + direction

            # Forward until linkling's eyes lost.
            on_eye = True
            while (x < x2) and (not on_eye):
                on_eye = img_eye_hist[x] > 128
                x = x + direction

            # If we found one, the inkling is between base_x and x.
            # Convert the value to relative position in the team,
            # and mark the corresponding inkling.
            #
            #              /  \  /  \  /  \  /  \
            #              |oo|  |oo|  |oo|  |oo|
            # inkling_x2: 0    25    50    75    100
            # team[x]   :   [0]   [1]   [2]   [3]
            #
            # FIXME: Inkling color detection is dropped.
            #
            if add_sample:
                inkling_x = int((x_base + x) / 2)
                inkling_x2 = int(((inkling_x - x1) / (x2 - x1)) * 100)
                if (inkling_x2 < 25):
                    if (team[0] is not None):
                        team[0] = True
                elif (inkling_x2 < 50):
                    if (team[1] is not None):
                        team[1] = True
                elif (inkling_x2 < 75):
                    if (team[2] is not None):
                        team[2] = True
                elif (inkling_x2 < 95):
                    if (team[3] is not None):
                        team[3] = True

            if 0:
                print(x_base, x)
                cv2.line(frame, (400 + x_base, 0),
                         (400 + x_base, 50), (0, 0, 255), 3)
                cv2.line(frame, (400 + inkling_x, 0),
                         (400 + inkling_x, 50), (0, 255, 0), 3)
        # The loop is over. Now team should have active inklings list.
        #   [ True, True, True, False ] ... 3 inklings are active.
        return team

    def _list2bitmap(self, list1, list2):
        l = list1.copy()
        l.extend(list2)

        bitmap = 0
        for i in range(len(l)):
            bitmap = bitmap + bitmap + (1 if l[i] else 0)

        return bitmap

    ##
    # _state_default
    #
    # In default state, this scene detects alive inklings and update
    # context['game']['inkling_state'].
    #
    # The format of context['game']['inkling_state'] is:
    #    [[team1a, team1b, team1c, team1d], [team2a, team2b, team2c, team2d ]]
    #
    # Each teamXx can be one of the values below.
    #    True:  The inkling is active, and alive.
    #    False: The inkling is actibe, but not alive
    #           (or disconnected from the game).
    #    None:  The inkling is inactive.
    #
    # This needs self.(my_|counter_) team fields intialized.
    #
    def _state_default(self, context):
        if self.is_another_scene_matched(context, 'GameTimerIcon') == False:
            if not self.matched_in(context, 20 * 1000):
                self._switch_state(self._state_start)
            return False

        frame = context['engine']['frame']
        if frame is None:
            return False

        vs_xpos = self._get_vs_xpos(context)
        if vs_xpos is None:
            return False

        my_team = self._find_inklings(
            context, 0, vs_xpos - 35, self.my_team)
        counter_team = self._find_inklings(
            context, vs_xpos + 35, self.meter_width_half * 2, self.counter_team)

        context['game']['inkling_state4'] = [my_team, counter_team]
        context['game']['inkling_state'] = [
            [e for e in my_team if e is not None],
            [e for e in counter_team if e is not None],
        ]

        bitmap = self._list2bitmap(my_team, counter_team)
        if self._last_bitmap != bitmap:
            self._call_plugins('on_game_inkling_state_update')
            self._last_bitmap = bitmap

        if 0:
            print(my_team, counter_team)
        if 0:
            cv2.line(frame, (self.meter_x1, 24 + 10),
                     (self.meter_x2, 24 + 10), (0, 0, 255), 1)
            cv2.line(frame, (self.meter_x1, 24 + 20),
                     (self.meter_x2, 24 + 20), (255, 0, 255), 1)
            cv2.line(frame, (self.meter_x1, 24 + 30),
                     (self.meter_x2, 24 + 30), (255, 0, 255), 1)
            cv2.line(frame, (self.meter_x1, 24 + 31),
                     (self.meter_x2, 24 + 31), (0, 0, 255), 1)
            cv2.imshow('frame', frame)
            cv2.waitKey(100)

        return True

    ##
    # _state_start
    #
    # This state will be activated at start the beginning of the game.
    # Purpose of this state is, to figure out which inklings are active.
    #
    # In public and ranked battles, we can assume all of the 8 inklings
    # are active. In 3-squad and private battles, some of the inklings
    # can be inactive.
    #
    # At the beginning of the game, all of the active inklings are alive.
    # This scene detects the active inklings and the fields:
    #     self.my_team
    #     self.counter_team
    #
    # If all of inklinkgs are active, the field should be:
    #     [ False, False, False, False ]
    # If our squad only has 3 inklings:
    #     [ False, False, False, None ]
    #
    # One the fields are set, this scene will switch to _state_default.
    #
    def _state_start(self, context):
        if self.is_another_scene_matched(context, 'GameTimerIcon') == False:
            return False

        frame = context['engine']['frame']
        if frame is None:
            return False

        vs_xpos = self._get_vs_xpos(context)
        if vs_xpos is None:
            return False

        my_team = self._find_inklings(context, 0, vs_xpos - 35)
        counter_team = self._find_inklings(
            context, vs_xpos + 35, self.meter_width_half * 2)

        for i in range(len(my_team)):
            my_team[i] = {True: False, False: None}[my_team[i]]

        for i in range(len(counter_team)):
            counter_team[i] = {True: False, False: None}[counter_team[i]]

        self.my_team = my_team
        self.counter_team = counter_team
        self._last_bitmap = None

        context['game']['inkling_state_at_start'] = [my_team, counter_team]
        self._switch_state(self._state_default)

        return True

    def _swtich_to_state_start(self, context):
        self.my_team = [False, False, False, False]
        self.counter_team = [False, False, False, False]

        return self._switch_state(self._state_start)

    def on_game_start(self, context):
        self._swtich_to_state_start(context)

    def on_game_go_sign(self, context):
        self._swtich_to_state_start(context)

    def _analyze(self, context):
        pass

    def dump(self, context):
        print('inkling state: %s vs %s' % (
            self._state_to_string(context['game']['inkling_state'][0]),
            self._state_to_string(context['game']['inkling_state'][1])
        ))

    def _init_scene(self, debug=False):
        self.my_team = [False, False, False, False]
        self.counter_team = [False, False, False, False]
        self._last_bitmap = None
