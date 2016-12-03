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

import ctypes
import numpy as np

from ikalog.utils.ikamatcher2.kernel import Kernel
from ikalog.utils.ikamatcher2.decode_1bit import decode_1bit
import ikamatcher2_neon_hal as ikamat2_neon


zeros512 = np.zeros(512, dtype=np.uint8)


class NEON(Kernel):
    # 128 bits for SIMD operation
    _align = 512

    def encode(self, img):
        """
        Encode the image to internal image format.

        Bits per pixel:               1bit (uint8)
        Alignment per lines:         0
        Alignment of returned image: self._align bytes
        """

        assert img.shape[0] == self._h
        assert img.shape[1] == self._w

        img_8b_1d = np.reshape(img, (-1))
        padding_len = self._align - (len(img_8b_1d) % self._align)
        if padding_len:
            img_8b_1d_p = np.append(img_8b_1d, zeros512[0: padding_len])
        else:
            img_8b_1d_p = img_8b_1d

        assert len(img_8b_1d_p.shape) == 1
        assert img_8b_1d_p.shape[0] >= (self._h * self._w / 8)
        assert img_8b_1d_p.shape[0] % self._align == 0

        dest = np.zeros(img_8b_1d_p.shape[0], dtype=np.uint8)
        ikamat2_neon.encode(dest, img_8b_1d_p, (self._h * self._w))
        return dest

    def decode(self, img):
        return decode_1bit(self, img)

    def popcnt(self, img):
        """
        Perform popcnt for the image.
        """
        width = 64
        pixels = self._w * self._h
        if (pixels % width):
            pixels += width - (pixels % width)

        assert pixels % width == 0
        assert pixels >= (self._w * self._h)

        assert len(img.shape) == 1
        assert img.shape[0] >= pixels / 8

        r = ikamat2_neon.logical_and_popcount_neon_256(img, pixels)
        return r

    def logical_or(self, img):
        raise Exception('not implemented')

    def logical_and(self, img):
        raise Exception('not implemented')

    def logical_andor_popcnt(self, img, width, func):
        pixels = self._w * self._h
        if (pixels % width):
            pixels += width - (pixels % width)

        assert pixels % width == 0
        assert pixels >= (self._w * self._h)

        assert len(img.shape) == 1
        assert img.shape[0] >= pixels / 8

        return func(img, self._img_mask, pixels)

    def logical_or_popcnt(self, img):
        return self.logical_andor_popcnt(img, 512, ikamat2_neon.logical_or_popcount_neon_512)

    def logical_and_popcnt(self, img):
        return self.logical_andor_popcnt(img, 512, ikamat2_neon.logical_and_popcount_neon_512)

