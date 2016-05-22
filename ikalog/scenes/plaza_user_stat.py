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
import sys

import cv2

from ikalog.utils import *


class PlazaUserStat(object):
    # 720p サイズでの値
    return_left = 35
    return_top = 633
    return_width = 72
    return_height = 63

    order_left = 876
    order_top = 623
    order_width = 113
    order_height = 32

    def match(self, context):
        if context['engine']['inGame']:
            return False

        src = context['engine']['frame']

        img_order = ImageUtils.crop_image_gray(
            src, self.order_left, self.order_top, self.order_width, self.order_height
        )

        if not ImageUtils.match_with_mask(img_order, self.mask_order, 0.85, 0.6):
            return False

        img_return = ImageUtils.crop_image_gray(
            src, self.return_left, self.return_top, self.return_width, self.return_height
        )

        if not ImageUtils.match_with_mask(img_return, self.mask_return, 0.85, 0.6):
            return False

        return True

    def __init__(self):
        self.mask_return = ImageUtils.load_mask(
            'masks/plaza_userstat.png', self.return_left, self.return_top, self.return_width, self.return_height)
        self.mask_order = ImageUtils.load_mask(
            'masks/plaza_userstat.png', self.order_left, self.order_top, self.order_width, self.order_height)

if __name__ == "__main__":

    print(sys.argv)
    target = cv2.imread(sys.argv[1])

    context = {"engine": {'frame': target, 'inGame': True}}
    obj = PlazaUserStat()

    r = obj.match(context)

    print(r)
