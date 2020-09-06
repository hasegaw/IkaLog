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

from ikalog.utils.image_filters.filters import MM_COLOR_BY_HUE
from ikalog.scenes.v2.game.inklings.transform import transform_inklings

_left_list = [0, 64, 128, 192]

"""
Parse information
"""
def is_alive(img):
    mask_inklings_black = cv2.inRange(img, (0, 0, 0), (30, 30, 30))
    black = np.sum(mask_inklings_black > 1)
    (h, w) = img.shape[0:2]
    black_ratio = black / (h*w)
    return black_ratio < 0.2

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


def extract_players(frame):
    img_teams = transform_inklings(frame)
    # cv2.imwrite('team1.png', img_teams['team1'])
    # cv2.imwrite('team2.png', img_teams['team2'])

    players_team1 = extract_players_image(img_teams['team1'])
    players_team2 = extract_players_image(img_teams['team2'])

    for player in players_team1:
        player['team'] = 0
        player['alive'] = is_alive(player['img_weapon'])
        player['index'] = players_team1.index(player)

    for player in players_team2:
        player['team'] = 1
        player['alive'] = is_alive(player['img_weapon'])
        player['index'] = 7 - players_team2.index(player)

    players = []
    players.extend(players_team1)
    players.extend(players_team2[::-1])

    return players


if __name__ == '__main__':
    import time
    import sys

    img = cv2.imread(sys.argv[1], 1)
    r = extract_players(img)

    t = time.time()
    i = 0
    for player in r:
        # if i == 0:
            for k in [
                'full',
                'img_weapon',
                # 'img_button',
                # 'img_special_charge',
                # 'img_kill_or_assist',
                # 'img_special'
                ]:
                cv2.imwrite('inklings.player%d.%s%s.png' %
                            (player['index'], 'splatted.' if player['splatted'] else '', k), player[k])

        # for k in ['weapon', 'kill_or_assist', 'special', 'score']:
        #     cv2.imwrite('scoreboard.player%d.%s.%s.png' %
        #                 (i, k, t), player['img_%s' % k])
            i = i + 1
