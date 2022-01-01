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

import requests
import json

from ikalog.utils import *

FX_SOLID = 0
FX_FLOW = 110
FX_BREATHE = 2
PALETTE_DEFAULT = 0
PALETTE_RAINBOW = 11

class WLED(object):

    ##
    # Creates initial color segments for a single squid lamp, with three groups of LEDs
    # Group 1: 8 LEDs. Swapped R & G channels from the wled settings
    # Group 2: 16 LEDs. RGB channels match the wled settings
    # Group 3: 6 LEDs. Swapped R & G channels from the wled settings
    ##
    def color_segments_for_player(self, player_index, team_color):
        return [
            {
                "id": player_index * 3,
                "on": True,
                "bri": 255,
                "fx": 0,
                "col": [
                    [team_color[1],team_color[0],team_color[2]] if player_index == 0 else  # first segment has swapped channels for R and G
                    [team_color[0],team_color[1],team_color[2]], # segment 2 matches the wled settings
                ],
                "start": player_index * 30,
                "stop":  player_index * 30 + 8,
            },
            {
                "id": player_index * 3 + 1,
                "on": True,
                "of": 2, # effect offset
                "col": [
                    [team_color[0],team_color[1],team_color[2]], # segment 2 matches the wled settings
                ],
                "pal": PALETTE_RAINBOW,
                "fx": 0,
                "sx": 128,
                "ix": 128,
                "start": player_index * 30 + 8,
                "stop":  player_index * 30 + 24,
            },
            {
                "id": player_index * 3 + 2,
                "on": True,
                "col": [
                    [255,255,255] # white
                ],
                "start": player_index * 30 + 24,
                "stop":  player_index * 30 + 30,
            }
        ]

    ##
    # Sets segment effects for a player 
    # If alive: All 3 segments on solid colors
    # If has special: second segment has a rainbow effect
    # If respawning: Segment 2 has a pulsing effect and segment 3 is dimmed
    ##
    def status_segments_for_player(self, player_index, is_alive, has_special):
        return [
            {
                "id": player_index * 3,
                "on": is_alive,
            },
            {
                "id": player_index * 3 + 1,
                "fx": FX_BREATHE if not is_alive else FX_FLOW if has_special else FX_SOLID,
                "pal": PALETTE_RAINBOW if has_special else PALETTE_DEFAULT,
            },
            {
                "id": player_index * 3 + 2,
                "bri": 255 if is_alive else 1
            }
        ]
    

    def light_team_color(self, context):
        if not self.team1_host and not self.team2_host:
            return

        if not ('team_color_rgb' in context['game']):
            return

        team1_color = context['game']['team_color_rgb'][0]
        team2_color = context['game']['team_color_rgb'][1]

        team1_segments = []
        team2_segments = []

        for i in range(4):
            team1_segments += self.color_segments_for_player(i, team1_color)
            team2_segments += self.color_segments_for_player(i, team2_color)

        print(json.dumps(team1_segments))

        try:
            if self.team1_host:
                requests.post(self.team1_host+'/json/state',
                timeout = 0.1, 
                data = json.dumps({
                    "seg": team1_segments
                }))
        except requests.Timeout:
            pass
        except requests.ConnectionError:
            pass
        except Exception as e:
            print(e)

        try:
            if self.team2_host:
                requests.post(self.team2_host+'/json/state',
                timeout = 0.1, 
                data = json.dumps({
                    "seg": team2_segments
                }))
        except requests.Timeout:
            pass
        except requests.ConnectionError:
            pass
            
        self.colors_set = True

    def on_frame_next(self, context):
        if not self.colors_set and self._in_game:
            self.light_team_color(context)

        # TODO Alecat: If requests fail, disable future requests and then poll for wled availability with incremental backoff


    def on_game_inkling_state_update(self, context):
        if not self.team1_host and not self.team2_host:
            return
        
        if not self.colors_set:
            return

        if not self._in_game:
            return

        team1_inkling_state = context['game']['inkling_state'][0]
        team1_inkling_specials = context['game']['inkling_state'][2]
        team2_inkling_state = context['game']['inkling_state'][1]
        team2_inkling_specials = context['game']['inkling_state'][3]

        if not len(team1_inkling_specials):
            return   

        team1_segments = []
        team2_segments = []
        for i in range(4):
            team1_segments += self.status_segments_for_player(i, team1_inkling_state[i], team1_inkling_specials[i])
            team2_segments += self.status_segments_for_player(i, team2_inkling_state[i], team2_inkling_specials[i])
        
        try:
            if self.team1_host:
                requests.post(self.team1_host+'/json/state',
                timeout = 0.1, 
                data = json.dumps({
                    "seg": team1_segments
                }))
        except requests.Timeout:
            pass
        except requests.ConnectionError:
            pass

        try:
            if self.team2_host:
                requests.post(self.team2_host+'/json/state',
                timeout = 0.1, 
                data = json.dumps({
                    "seg": team2_segments
                }))
        except requests.Timeout:
            pass
        except requests.ConnectionError:
            pass

    def on_game_go_sign(self, context):
        self._in_game = True
        self.colors_set = False

    def on_game_finish(self, context):
        self._in_game = False
        self.light_team_color(context)

    def on_result_judge(self, context):
        team1_win = context['game']['won']
        team1_segments = []
        team2_segments = []
        for i in range(4):
            team1_segments += self.status_segments_for_player(i, bool(team1_win), bool(team1_win))
            team2_segments += self.status_segments_for_player(i, not bool(team1_win), not bool(team1_win))
        
        try:
            if self.team1_host:
                requests.post(self.team1_host+'/json/state',
                timeout = 0.1, 
                data = json.dumps({
                    "seg": team1_segments
                }))
        except requests.Timeout:
            pass
        except requests.ConnectionError:
            pass

        try:
            if self.team2_host:
                requests.post(self.team2_host+'/json/state',
                timeout = 0.1, 
                data = json.dumps({
                    "seg": team2_segments
                }))
        except requests.Timeout:
            pass
        except requests.ConnectionError:
            pass
            

    ##
    # Constructor
    # @param self       The Object Pointer.
    # @param team1_host wled URL for the alpha team light array (optional)
    # @param team1_host wled URL for the bravo team light array (optional)
    #
    def __init__(self, team1_host=None, team2_host=None):
        self.team1_host = team1_host
        self.team2_host = team2_host
        self._in_game = False
        self.colors_set = False

if __name__ == "__main__":
    obj = WLED(team1_host='http://192.168.0.114')


    context = {
        'game': {
            'inGame': True,
            'team_color_rgb': [(203, 23, 170), (0, 255, 0)],
        }
    }
    obj.on_game_go_sign(context)
    obj.light_team_color(context)
