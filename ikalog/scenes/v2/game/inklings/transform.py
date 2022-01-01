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
from blend_modes import subtract

inklings_y_offset = 11

inklings_team1_x_offset = 330
inklings_team2_x_offset = 695

inklings_box_width = 255
inklings_box_height = 80

bar_y_offset = 49
bar_height = 4

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

    # team_bar_hsv = cv2.cvtColor(team_bar, cv2.COLOR_BGR2HSV)
    # dark_pixel_mask = cv2.inRange(team_bar_hsv, (0, 0, 0), (180, 255, 50))
    gray_team_bar = cv2.cvtColor(team_bar, cv2.COLOR_BGR2GRAY)
    dark_pixel_mask = cv2.inRange(gray_team_bar, 0, 80)
    dark_pixels = np.sum(dark_pixel_mask > 1)

    total_count = bar_height * bar_check_extent_width
    # print("Dark count", dark_pixels, total_count, dark_pixels/total_count, team_index)
    # cv2.imwrite('pimg/%s.png' % team_index, team_bar)
    # cv2.imwrite('pimg/%s.dark.png' % team_index, dark_pixel_mask)

    return dark_pixels/total_count


"""
TODO Alecat: reimplement team weight using colour data?
"""
def analyze_team_weight_2(img_team, team_index, team_color_rgb):
    img_team = copy.deepcopy(img_team)
    x_offset = 10 if not team_index else inklings_box_width - 10 - bar_check_extent_width

    # KO'd inklings are near pure black - highlight them
    mask_inklings_black = cv2.inRange(img_team, (0, 0, 0), (10, 10, 10))
    img_team[mask_inklings_black > 0] = (255, 255, 255)

    # if available - find team coloured areas
    # if team_color_rgb:
    #     mask_team_colour = cv2.inRange(img_team, (team_color_rgb[2]-50,team_color_rgb[1]-50,team_color_rgb[0]-50), (team_color_rgb[2]+50,team_color_rgb[1]+50,team_color_rgb[0]+50))
    #     img_team[mask_team_colour > 0] = (255, 255, 255)

    # # danger starburst has a greenish colour - ignore this green
    # # Note - hopefully we don't have any team colors that are too close to this green...?
    img_team_hsv = cv2.cvtColor(img_team, cv2.COLOR_BGR2HSV)
    mask_team_danger = cv2.inRange(img_team_hsv, (30,128,0), (50,255,255))
    img_team[mask_team_danger > 0] = (0, 0, 0)

    # team_color_contours, _ = cv2.findContours(mask_team_colour, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)

    gray = cv2.cvtColor(img_team, cv2.COLOR_BGR2GRAY)
    # get threshold on inversion
    _, roi = cv2.threshold(255-gray, 200, 255, cv2.THRESH_BINARY)
    threshold_contours, _ = cv2.findContours(roi, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
    
    contours_filled = np.zeros( img_team.shape )
    cv2.fillPoly(contours_filled, pts =threshold_contours, color=(255,255,255))

    team_bar = contours_filled[bar_y_offset:bar_y_offset+bar_height, x_offset:x_offset+bar_check_extent_width]

    dark_pixel_mask = cv2.inRange(team_bar, 0, 10)
    dark_pixels = np.sum(dark_pixel_mask < 1)

    # cv2.imwrite('pimg/%s.maskteam.png' % team_index, mask_team_colour)
    # cv2.imwrite('pimg/%s.contours.png' % team_index, contours_filled)
    # cv2.imwrite('pimg/%s.bar.png' % team_index, team_bar)
    # cv2.imwrite('pimg/%s.png' % team_index, dark_pixel_mask)

    total_count = bar_height * bar_check_extent_width

    return dark_pixels/total_count

def transform_inklings(frame, context):
    # Given an image, determine the weighting of the squid sizes so that details can be determined
    team1 = frame[inklings_y_offset: inklings_y_offset + inklings_box_height, inklings_team1_x_offset : inklings_team1_x_offset + inklings_box_width]
    team2 = frame[inklings_y_offset: inklings_y_offset + inklings_box_height, inklings_team2_x_offset : inklings_team2_x_offset + inklings_box_width]

    if 'team_color_rgb' in context['game']:
        # team1_weight = analyze_team_weight_2(team1, 0, context['game']['team_color_rgb'][0])
        # team2_weight = analyze_team_weight_2(team2, 1, context['game']['team_color_rgb'][1])
        team1_weight = analyze_team_weight(team1, 0)
        team2_weight = analyze_team_weight(team2, 1)
    else:
        return {
            'scenario': 'none',
            'team1': None,
            'team2': None,
        }

    # print(team1_weight, team2_weight)
    if team1_weight > 0.9 or (team1_weight > 0.7 and team2_weight < 0.2):
        return {
            'scenario': 'team1 danger',
            'team1': cv2.resize(team1[8:8+team_danger_size[1],52:52+team_danger_size[0]], (inklings_box_width, inklings_box_height)),
            'team2': team2,
        }
    elif team2_weight > 0.9 or (team2_weight > 0.7 and team1_weight < 0.2):
        return {
            'scenario': 'team2 danger',
            'team1': team1,
            'team2': cv2.resize(team2[8:8+team_danger_size[1],3:3+team_danger_size[0]], (inklings_box_width, inklings_box_height)),
        }
    elif team1_weight > 0.7 and team2_weight < 0.5:
        return {
            'scenario': 'team2 advantage',
            'team1': cv2.resize(team1[2:2+team_disadvantage_size[1],14:14+team_disadvantage_size[0]], (inklings_box_width, inklings_box_height)),
            'team2': cv2.resize(team2[5:5+team_advantage_size[1],4:4+team_advantage_size[0]], (inklings_box_width, inklings_box_height)),
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
    context = {
        'game' : {
            'team_color_rgb': [
                # (123, 3, 147), # PURPLE
                # (67, 186, 5), # LUMIGREEN
                # (41, 34, 181),
                # (94, 182, 4), # GREEN
                (217, 193, 0), # YELLOW
                (0, 122, 201), # LIGHTBLUE
            ],
        }
    }
    r = transform_inklings(img, context)

    print(r['scenario'])
    cv2.imshow('left', r['team1'])
    cv2.waitKey()
    cv2.imshow('right', r['team2'])
    cv2.waitKey()
