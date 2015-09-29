#!/usr/bin/env python3
# -*- coding: utf-8 -*-
#
#  IkaLog
#  ======
#  Copyright (C) 2015 Takeshi HASEGAWA
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
import pickle

from ikalog.utils.character_recoginizer.character import *
from ikalog.utils.character_recoginizer.number import *
from ikalog.utils.character_recoginizer.udemae import *


array0to1280 = np.array(range(1280), dtype=np.int32)


class FixedWidth(object):
    # not implemented yet.
    left = 0
    right = 1
    center = 2

    def __init__(self, width, align=left):
        assert align in [self.left, self.right, self.center]
        self.width = width
        self.align = align


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
                    chars.append((x_start, x - 1))
                    in_char = False
            else:
                if img_hist_x[x] > 0:
                    x_start = x
                    in_char = True
                else:
                    continue

        return chars

    def __init__(self):
        pass

# FixMe: should be moved to test/

if __name__ == "__main__":
    import sys
    files = sys.argv[1:]

    total = 0
    number_recoginizer = NumberRecoginizer()
    number_recoginizer.save_model_to_file('data/number.model')
    udemae_recoginizer = UdemaeRecoginizer()
    udemae_recoginizer.save_model_to_file('data/udemae.model')

#    for d in data:
#        r = obj.matchSingleDigit(d['img'])
#        print(d['file'], r)

    for file in files:
        target = cv2.imread(file)
        cv2.imshow(file, target)

        num = None
        ude = None

        num = number_recoginizer.match(target)
        ude = udemae_recoginizer.match(target)
        print(file, num, ude)

        for sample in number_recoginizer.find_samples(target):
            cv2.imwrite('/tmp/_samples%d.png' % total, sample)
            total = total + 1

    if total > 0:
        cv2.waitKey()
