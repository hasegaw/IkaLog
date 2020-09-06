#!/usr/bin/env python3
# -*- coding: utf-8 -*-
#
#  IkaLog
#  ======
#  Copyright (C) 2015 Takeshi HASEGAWA, Junki MIZUSHIMA
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

_center = (int(1280 * 0.75), int(720 * 0.5))
_top_win = 57
_top_lose = 390
_height = 300

mat_win_team = cv2.getRotationMatrix2D(_center, -2.5, 1.0)
mat_lose_team = cv2.getRotationMatrix2D(_center, 2.0, 1.0)


def transform_scoreboard(frame):
    assert frame.shape[0] == 720
    assert frame.shape[1] == 1280

    # dim = (frame.shape[1], frame.shape[0])

    # img_win_team = cv2.warpAffine(frame, mat_win_team, dim)
    # cv2.imwrite('win.png', img_win_team)
    # img_lose_team = cv2.warpAffine(frame, mat_lose_team, dim)

    # return {
    #     'win': img_win_team[_top_win:_top_win + _height, 639:, :],
    #     'lose': img_lose_team[_top_lose:_top_lose + _height, 639:, :],
    # }

    # scoreboard_win = np.float32([[628.157,72.222],[1225.721,49.396],[1236.886,341.683],[639.322,364.509]])
    # scoreboard_lose = np.float32([[639.604,381.604],[1237.235,402.591],[1226.97,694.911],[629.338,673.924]])
    scoreboard_win = np.float32([[628.77,72.249],[1227.465,49.329],[1238.773,341.702],[639.884,364.523]])
    scoreboard_lose = np.float32([[639.162,381.005],[1238.585,402.556],[1228.858,695.257],[630.405,673.381]])
    team_target_dimensions = np.float32([[0,0],[530,0],[530,300],[0,300]])

    M1 = cv2.getPerspectiveTransform(scoreboard_win,team_target_dimensions)
    win = cv2.warpPerspective(frame,M1,(530,300))
    M2 = cv2.getPerspectiveTransform(scoreboard_lose,team_target_dimensions)
    lose = cv2.warpPerspective(frame,M2,(530,300))

    return {
        'win' : win,
        'lose': lose
    }



if __name__ == '__main__':
    import sys

    img = cv2.imread(sys.argv[1], 1)
    print(img.shape)
    r = transform_scoreboard(img)
    # cv2.imshow('win', r['win'])
    # cv2.imshow('lose', r['lose'])

    cv2.imwrite('win.png', r['win'])
    cv2.imwrite('lose.png', r['lose'])

    cv2.waitKey()
