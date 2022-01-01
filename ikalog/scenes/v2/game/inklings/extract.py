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

import cv2
import numpy as np
import blend_modes
import time

from ikalog.utils.image_filters.filters import MM_COLOR_BY_HUE
from ikalog.scenes.v2.game.inklings.transform import transform_inklings

_left_list = [0, 64, 128, 192]
_lastScreenshotted = 0

"""
Parse information
"""
def is_alive(img):
    mask_inklings_black = cv2.inRange(img, (0, 0, 0), (30, 30, 30))
    black = np.sum(mask_inklings_black > 1)
    (h, w) = img.shape[0:2]
    black_ratio = black / (h*w)
    return black_ratio < 0.2



def is_special(img, team_color, screenshot = False):
    global _lastScreenshotted
    # analyse just a subset of the image
    # a small segment of the icon that should exclude the weapon and other UI elements
    # named "baseline" as it is across the team line
    baseline = img[55:55+3, 21:21+20, :]
    # image with alpha channel
    rgba = cv2.cvtColor(baseline, cv2.COLOR_RGB2RGBA)

    (h, w) = baseline.shape[0:2]
    # layer with team color
    img_layer = np.zeros((h, w, 4), np.uint16) + [team_color[2],team_color[1],team_color[0],255]

    # apply difference blend mode of gameplay colour over the image
    difference = blend_modes.difference(rgba.astype(float), img_layer.astype(float), 1)

    # if the result is black - the player is alive but has no special
    mask_inklings_greyscale = cv2.cvtColor(difference.astype('float32'), cv2.COLOR_RGBA2GRAY)
    mask_inklings_black = cv2.inRange(mask_inklings_greyscale, 0, 40)
    black = np.sum(mask_inklings_black > 1)
    black_ratio = black / (h*w)
    alive = black_ratio > 0.6
    special = False

    if not alive:
        # if the result doesn't match the team color - the player has special
        mask_inklings_team = cv2.inRange(difference, (team_color[2]-10,team_color[1]-10,team_color[0]-10, 255), (team_color[2]+10,team_color[1]+10,team_color[0]+10, 255))
        team_colored = np.sum(mask_inklings_team > 1)
        team_ratio = team_colored / (h*w)
        special = alive = team_ratio < 0.5
    
    # Write debug images
    screenshot_time = time.time()
    if screenshot and screenshot_time > _lastScreenshotted + 5:
        # cv2.imwrite("pimg/%s.%s.%s.png" % (screenshot_time, 'alive' if alive else 'splatted','special' if special else ''), img)
        # cv2.imwrite("pimg/%s.diff.%s.%s.png" % (screenshot_time, 'alive' if alive else 'splatted','special' if special else ''), difference)
        _lastScreenshotted = screenshot_time

    return [special, alive]
"""
Entry extraction
"""


def extract_entry(img_entry):
    return {
        'full': img_entry,
        'img_kill_or_assist': img_entry[0:17, 0:20, :],
        'img_special': img_entry[0:17, 40:40+20, :],
        'img_weapon': img_entry[20:20+37, 4:55, :],
        'img_button': img_entry[55:55+26, 0:26, :],
        'img_special_charge': img_entry[58:58+22, 30:30+33, :],
    }


def extract_players_image(img_team):
    players = []

    for left in _left_list:
        img_entry = img_team[:, left:left+63, :]
        e = extract_entry(img_entry)
        players.append(e)
    return players


def extract_players(frame, context):
    img_teams = transform_inklings(frame, context)
    # cv2.imwrite('team1.png', img_teams['team1'])
    # cv2.imwrite('team2.png', img_teams['team2'])
    if img_teams['scenario'] == 'none':
        return []

    players_team1 = extract_players_image(img_teams['team1'])
    players_team2 = extract_players_image(img_teams['team2'])

    screenshot = True
    for player in players_team1:
        player['team'] = 0
        player['alive'] = is_alive(player['img_weapon'])
        if 'team_color_rgb' in context['game']:
            player['special'] = player['alive'] and is_special(player['full'], context['game']['team_color_rgb'][0], screenshot)[0]
            screenshot = False
        player['index'] = players_team1.index(player)

    for player in players_team2:
        player['team'] = 1
        player['alive'] = is_alive(player['img_weapon'])
        if 'team_color_rgb' in context['game']:
            player['special'] = player['alive'] and is_special(player['full'], context['game']['team_color_rgb'][1])[0]
        player['index'] = 7 - players_team2.index(player)

    players = []
    players.extend(players_team1)
    players.extend(players_team2[::-1])

    return players


if __name__ == '__main__':
    import time
    import sys

    img = cv2.imread(sys.argv[1], 1)
    context = {
        'game' : {
            'team_color_rgb': [
                # (123, 3, 147), # PURPLE
                # (67, 186, 5), # LUMIGREEN
                (217, 193, 0), # YELLOW
                (0, 122, 201), # LIGHTBLUE
                # (221, 152, 14), # YELLOW
                # (156, 8, 190), # PURPLE
            ]
        }
    }
    r = extract_players(img, context)

    t = time.time()
    i = 0
    for player in r:
            print( player['team'], 'alive:', player['alive'], 'special:', player['special'])
        # if i == 0:
            # for k in [
            #     'full',
            #     'img_weapon',
            #     # 'img_button',
            #     # 'img_special_charge',
            #     # 'img_kill_or_assist',
            #     # 'img_special'
            #     ]:
            #     cv2.imwrite('inklings.player%d.%s%s.png' %
            #                 (player['index'], 'splatted.' if player['splatted'] else '', k), player[k])

        # for k in ['weapon', 'kill_or_assist', 'special', 'score']:
        #     cv2.imwrite('scoreboard.player%d.%s.%s.png' %
        #                 (i, k, t), player['img_%s' % k])
            i = i + 1
