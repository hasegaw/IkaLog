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


_width, _height = 278, 209
_left = (291, 534, 534 + (534 - 291))
_top = 280

_top_win = 57
_top_lose = 390
_height = 300
_center = (0, 0)
mat_wave = cv2.getRotationMatrix2D(_center, -5.0, 1.0)


def transform_scoreboard(frame):
    assert frame.shape[0] == 720
    assert frame.shape[1] == 1280
    r = []

    for i in range(len(_left)):
        left = _left[i]

        img_wave = frame[_top: _top + _height, left: left + _width]

        dim = (img_wave.shape[1], img_wave.shape[0])
        img_wave_t = cv2.warpAffine(img_wave, mat_wave, dim)

        r.append(img_wave_t)

    return r


def extract(img_wave):

    img_count = img_wave[34: 34 + 74, 13: 13 + 199]
    img_count_hsv = cv2.cvtColor(img_count, cv2.COLOR_BGR2HSV)
    img_count_gray = img_count_hsv[:, :, 2]
    img_count_gray[img_count_hsv[:, :, 1] > 30] = 0

    #img_count_gray = cv2.cvtColor(img_count, cv2.COLOR_BGR2GRAY)
    img_count_gray[img_count_gray < 200] = 0
    img_count_gray[img_count_gray > 0] = 255

    from ikalog.ml.text_reader import TextReader
    _tr = TextReader()
    s = _tr.read_char(img_count_gray, crop_min_per_char=True)
    print(s)


if __name__ == '__main__':
    img = cv2.imread(
        #        '/Users/t-hasegawa/Pictures/vlcsnap-2017-07-30-21h56m50s466.png', 1)
        '/Users/t-hasegawa/Pictures/vlcsnap-2017-07-25-02h21m27s308.png', 1)
    print(img.shape)
    r = transform_scoreboard(img)
    for i in range(len(r)):
        cv2.imshow(str(i), r[i])
        cv2.imwrite('eggs%d.png', r[i])
        extract(r[i])
    cv2.waitKey()
