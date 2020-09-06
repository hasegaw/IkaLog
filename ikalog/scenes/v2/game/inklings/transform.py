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
import copy

inklings_y_offset = 11

inklings_team1_x_offset = 330
inklings_team2_x_offset = 695

inklings_box_width = 255
inklings_box_height = 80

bar_y_offset = 47
bar_height = 6

bar_check_extent_width = 45

team_advantage_size = (241, 78)
team_neutral_size = (228, 73)
team_disadvantage_size = (214, 69)
team_danger_size = (199, 63)

"""
Entry extraction
"""


def analyze_team_weight(img_team, team_index):
    img_team = copy.deepcopy(img_team)

    x_offset = 10 if not team_index else inklings_box_width - 10 - bar_check_extent_width
    team_bar = img_team[bar_y_offset:bar_y_offset+bar_height, x_offset:x_offset+bar_check_extent_width]

    # Replace absolute black & some greys in the bar with white - this is a KO'd player
    mask_inklings_black = cv2.inRange(team_bar, (0, 0, 0), (3, 3, 3))
    mask_inklings_weapon = cv2.inRange(team_bar, (184, 184, 184), (190, 190, 190))
    mask_inklings_cross = cv2.inRange(team_bar, (90, 90, 90), (100, 100, 100))
    team_bar[mask_inklings_black > 0] = (255, 255, 255)
    team_bar[mask_inklings_weapon > 0] = (255, 255, 255)
    team_bar[mask_inklings_cross > 0] = (255, 255, 255)

    team_bar_hsv = cv2.cvtColor(team_bar, cv2.COLOR_BGR2HSV)
    dark_pixel_mask = cv2.inRange(team_bar_hsv, (0, 0, 0), (180, 255, 50))
    dark_pixels = np.sum(dark_pixel_mask > 1)

    total_count = bar_height * bar_check_extent_width
    # print("Dark count", dark_pixels, total_count, dark_pixels/total_count, team_index)

    return dark_pixels/total_count





def transform_inklings(frame):
    # Given an image, determine the weighting of the squid sizes so that details can be determined
    team1 = frame[inklings_y_offset: inklings_y_offset + inklings_box_height, inklings_team1_x_offset : inklings_team1_x_offset + inklings_box_width]
    team2 = frame[inklings_y_offset: inklings_y_offset + inklings_box_height, inklings_team2_x_offset : inklings_team2_x_offset + inklings_box_width]

    team1_weight = analyze_team_weight(team1, 0)
    team2_weight = analyze_team_weight(team2, 1)
    if team1_weight > 0.9 or (team1_weight > 0.7 and team2_weight < 0.2):
        return {
            'scenario': 'team1 danger',
            'team1': cv2.resize(team1[8:8+team_danger_size[1],52:52+team_danger_size[0]], (inklings_box_width, inklings_box_height)),
            'team2': team2,
        }
    elif team2_weight > 0.9 or (team2_weight > 0.7 and team1_weight < 0.2   ):
        return {
            'scenario': 'team2 danger',
            'team1': team1,
            'team2': cv2.resize(team2[8:8+team_danger_size[1],3:3+team_danger_size[0]], (inklings_box_width, inklings_box_height)),
        }
    elif team1_weight > 0.7 and team2_weight < 0.5:
        return {
            'scenario': 'team2 advantage',
            'team1': team1,
            'team2': team2,
        }
    elif team2_weight > 0.7 and team1_weight < 0.5:
        return {
            'scenario': 'team1 advantage',
            'team1': cv2.resize(team1[2:2+team_advantage_size[1],14:14+team_advantage_size[0]], (inklings_box_width, inklings_box_height)),
            'team2': cv2.resize(team2[5:5+team_disadvantage_size[1],4:4+team_disadvantage_size[0]], (inklings_box_width, inklings_box_height)),
        }

    return {
        'scenario': 'neutral',
        'team1': cv2.resize(team1[4:4+team_neutral_size[1],26:26+team_neutral_size[0]], (inklings_box_width, inklings_box_height)),
        'team2': cv2.resize(team2[4:4+team_neutral_size[1],2:2+team_neutral_size[0]], (inklings_box_width, inklings_box_height)),
    }


if __name__ == '__main__':
    import sys

    img = cv2.imread(sys.argv[1], 1)
    r = transform_inklings(img)

    print(r['scenario'])
    cv2.imshow('left', r['team1'])
    cv2.waitKey()
    cv2.imshow('right', r['team2'])
    cv2.waitKey()
