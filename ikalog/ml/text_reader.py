#!/usr/bin/env python3
# -*- coding: utf-8 -*-
#
#  IkaLog
#  ======
#  Copyright (C) 2015- Takeshi HASEGAWA and IkaLog developers
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

import time

import cv2
import numpy as np

from ikalog.ml import classifier


_array0to1280 = np.array(range(1280), dtype=np.int32)

def get_min_and_max(array_2d):
    """
    ゼロエリアを除いた最小枠を求める
    """
    # print(array_2d.shape)
    sum_y = np.sum(array_2d, axis=1)
    sum_x = np.sum(array_2d, axis=0)
    # print(sum_x)
    # print(sum_y)

    x_pixels = np.extract(sum_x > 0, _array0to1280)
    y_pixels = np.extract(sum_y > 0, _array0to1280)
    #print('x_pixels', x_pixels)
    #print('y_pixels', y_pixels)

    # FIXME: 例外
    #print('restule', x_pixels[0], y_pixels[0], x_pixels[-1], y_pixels[-1])

    if len(x_pixels) == 0 or len(y_pixels) == 0:
        return None

    return x_pixels[0], y_pixels[0], x_pixels[-1] + 1, y_pixels[-1] + 1


class PerCharacter(object):

    def cut(self, img, img_hist_x):
        chars = []
        in_char = False
        x_start = None
        last_x = None

        for x in range(len(img_hist_x)):
            if in_char:
                if img_hist_x[x] > 0:
                    continue
                else:
                    char = (x_start, x - 1)
                    if char[1] - char[0] > 2:
                        chars.append((x_start, x - 1))
                    in_char = False
            else:
                if img_hist_x[x] > 0:
                    x_start = x
                    in_char = True
                else:
                    continue
        if in_char:
            chars.append((x_start, x))

        return chars


class TextReader(object):
    def __init__(self):
        self._c = classifier.ImageClassifier()
        self._c.load_from_file('data/spl2/spl2.font2.dat')

    def read_int(self, img, verbose=False, crop_min_per_char=False):
        val_str, val_int = None, None
        val_str = self.read_char(img)
        try:
            val_int = int(val_str)
        except:
            pass
        return val_int

    def read_char(self, img, verbose=False, crop_min_per_char=False):
        rect = get_min_and_max(img)
        if rect is None:
            return None
        x1, y1, x2, y2 = rect
        img = img[y1:y2, x1: x2]

        img_hist_x = np.sum(img, axis=0)

        z = PerCharacter().cut(img, img_hist_x)

        img_char_list = list(map(lambda t: img[:, t[0]:t[1]], z))

        img_char_f_list = []

        s = ''
        i = 0
        for i in range(len(img_char_list)):
            c = img_char_list[i]
            if crop_min_per_char:
                rect = get_min_and_max(c)
                if rect is None:
                    return None
                x1, y1, x2, y2 = rect
                c = c[y1:y2, x1: x2]

            #cv2.imshow('text_read', c)
            # cv2.waitKey()

            if verbose:
                cv2.imshow('image', c)
            c = cv2.resize(c, self._c._resize)
            c = cv2.cvtColor(c, cv2.COLOR_GRAY2BGR)
            # print(c.shape)
            y = self._c.predict1_index(c)

            if y >= 0:
                s = "%s%s" % (s, self._c._labels[y])
                _l = str(y)
            else:
                print('%d 文字目が読めない' % i)
                _l = 'confused'
                # return None

            if verbose:
                print(y)
                cv2.waitKey(1000)

            # cv2.imwrite('number.%s.%s.png' %
            #             (_l, time.time()), img_char_list[i])
        # print('result', s)

        return s
