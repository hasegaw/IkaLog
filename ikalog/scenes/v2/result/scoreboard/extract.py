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
from ikalog.scenes.v2.result.scoreboard.transform import transform_scoreboard

_top_list = [66, 121, 177, 232]

"""
Arrow Detection
"""


def find_my_entry_index(all_players):
    def loss_func(p): return np.sum(image_filters.MM_DARK()(p['img_selected']))
    losses = list(map(loss_func, all_players))
    return np.argmin(losses)


def find_my_entry(all_players):
    return all_players[find_my_entry_index(all_players)]


"""
Entry extraction
"""


def extract_entry(img_entry):
    hh = int(img_entry.shape[0] * 0.52)
    return {
        'img_selected': img_entry[:, 45:45 + 30, :],
        'img_player': img_entry[:, 105:105 + 50, :],
        'img_weapon': img_entry[:, 195: 195 + 45, :],
        'img_name': img_entry[:, 197: 192 + 200, :],
        'img_score': img_entry[:, 390:390 + 100, :],
        'img_kill_or_assist': img_entry[hh:, 515: 515 + 30, :],
        'img_special': img_entry[hh:, 561: 561 + 30, :],
    }


def extract_players_image(img_team):
    players = []

    for top in _top_list:
        img_entry = img_team[top: top + 47, :, :]
        e = extract_entry(img_entry)
        players.append(e)
    return players


def is_selected(img_selected):
    f = MM_COLOR_BY_HUE(hue=(33 - 5, 33 + 5), visibility=(230, 255))
    score = np.sum(f(img_selected)) / 255
    return score > 200


def extract_players(frame):
    img_teams = transform_scoreboard(frame)

    players_win = extract_players_image(img_teams['win'])
    players_lose = extract_players_image(img_teams['lose'])

    for player in players_win:
        player['team'] = 0
        player['index'] = players_win.index(player)
        player['myself'] = is_selected(player['img_selected'])

    for player in players_lose:
        player['team'] = 1
        player['index'] = players_lose.index(player) + 4
        player['myself'] = is_selected(player['img_selected'])

    players = []
    players.extend(players_win)
    players.extend(players_lose)

    return players


if __name__ == '__main__':
    import time

    img = cv2.imread(
        '/Users/hasegaw/Dropbox/project_IkaLog/v2/raw_images/ja/result_socreboard.png', 1)
    r = extract_players(img)

    t = time.time()
    i = 0
    for player in r:
        for k in ['weapon', 'kill', 'death']:
            cv2.imwrite('scoreboard.player%d.%s.%s.png' %
                        (i, k, t), player['img_%s' % k])
        i = i + 1
