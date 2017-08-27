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


def extract_team_colors(context, img):
    assert 'won' in context['game']
    assert len(img.shape) >= 2
    assert img.shape[0] == 720
    assert img.shape[1] == 1280

    team0_color_bgr = img[53, 975].reshape(1, 1, 3)
    team1_color_bgr = img[395, 995].reshape(1, 1, 3)

    my_team_color_bgr, counter_team_color_bgr = \
        (team0_color_bgr, team1_color_bgr) if context['game']['won'] \
        else (team1_color_bgr, team0_color_bgr)

    my_team_color = {
        'rgb': cv2.cvtColor(my_team_color_bgr, cv2.COLOR_BGR2RGB).tolist()[0][0],
        'hsv': cv2.cvtColor(my_team_color_bgr, cv2.COLOR_BGR2HSV).tolist()[0][0],
    }

    counter_team_color = {
        'rgb': cv2.cvtColor(counter_team_color_bgr, cv2.COLOR_BGR2RGB).tolist()[0][0],
        'hsv': cv2.cvtColor(counter_team_color_bgr, cv2.COLOR_BGR2HSV).tolist()[0][0],
    }

    return (my_team_color, counter_team_color)
