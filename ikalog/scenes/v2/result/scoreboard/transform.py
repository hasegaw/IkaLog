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

_center = (int(1280 * 0.75), int(720 * 0.5))
_top_win = 61
_top_lose = 404
_height = 300

mat_win_team = cv2.getRotationMatrix2D(_center, -2.0, 1.0)
mat_lose_team = cv2.getRotationMatrix2D(_center, 2.0, 1.0)


def transform_scoreboard(frame):
    #assert frame.shape[0] == 720
    #assert frame.shape[1] == 1280

    dim = (frame.shape[1], frame.shape[0])

    img_win_team = cv2.warpAffine(frame, mat_win_team, dim)
    img_lose_team = cv2.warpAffine(frame, mat_lose_team, dim)

    return {
        'win': img_win_team[_top_win:_top_win + _height, 640:, :],
        'lose': img_lose_team[_top_lose:_top_lose + _height, 640:, :],
    }

if __name__ == '__main__':
    img = cv2.imread(
        '/Users/hasegaw/Dropbox/project_IkaLog/v2/raw_images/ja/result_socreboard.png', 1)
    print(img.shape)
    r = transform_scoreboard(img)
    cv2.imshow('win', r['win'])
    cv2.imshow('lose', r['lose'])

    cv2.imwrite('/tmp/win.png', r['win'])
    cv2.imwrite('/tmp/lose.png', r['lose'])

    cv2.waitKey()
