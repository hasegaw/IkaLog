#!/usr/bin/env python3
# -*- coding: utf-8 -*-
#
#  IkaLog
#  ======
#  Copyright (C) 2015-2016 Takeshi HASEGAWA
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

import numpy as np


def decode_1bit(self, img):
    """
    Decode the image from popcnt internal image format.
    """
    assert len(img.shape) == 1
    assert img.shape[0] >= (self._h * self._w / 8)
    assert img.shape[0] % self._align == 0

    bitrev8 = lambda x: sum(1 << (8 - 1 - i) for i in range(8) if x >> i & 1)
    img_reverse = np.array(
        list(map(lambda x: bitrev8(x), img)), dtype=np.uint8)

    img_8b_1d = np.unpackbits(img_reverse) * 255  # to 8bit gray scale.
    img_8b_1d_trimmed = img_8b_1d[0: (self._h * self._w)]
    img_8b_2d = np.reshape(img_8b_1d_trimmed, (self._h, self._w))

    return img_8b_2d
