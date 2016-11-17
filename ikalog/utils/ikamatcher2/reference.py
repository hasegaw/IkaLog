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
import time
import cv2

from ikalog.utils.ikamatcher2.kernel import Kernel


class Numpy_uint8(Kernel):
    zeros128 = np.zeros(128, dtype=np.uint8)
    _align = 128

    def encode(self, img):
        """
        Encode the image to internal image format.

        Bits per pixel:               8bit (uint8)
        Alignment per lines:         0
        Alignment of returned image: self._align bytes
        """

        assert img.shape[0] == self._h
        assert img.shape[1] == self._w

        return img

    def decode(self, img):
        """
        Decode the image from internal image format.
        """

        assert img.shape[0] == self._h
        assert img.shape[1] == self._w

        return img

    def logical_or(self, img=None):
        r = np.maximum(self._img_mask, img)
        return r

    def logical_and(self, img=None):
        r = np.minimum(self._img_mask, img)
        return r

    def popcnt(self, img):
        hist = cv2.calcHist([img], [0], None, [3], [0, 256])
        return hist[2]


class Numpy_uint8_fast(Numpy_uint8):

    def logical_or(self, img=None):
        r = self._img_mask | img
        return r

    def logical_and(self, img=None):
        r = self._img_mask & img
        return r


class Numpy_1bit(Kernel):
    # 128 bits for SIMD operation
    _align = 16
    zeros128 = np.zeros(128, dtype=np.uint8)

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
        img_1b_1d = np.packbits(img_8b_1d)

        padding_len = self._align - (len(img_1b_1d) % self._align)
        if padding_len:
            img_1b_1d_p = np.append(img_1b_1d, self.zeros128[0: padding_len])
        else:
            img_1b_1d_p = img_1b_1d

        assert len(img_1b_1d_p.shape) == 1
        assert img_1b_1d_p.shape[0] >= (self._h * self._w / 8)
        assert img_1b_1d_p.shape[0] % self._align == 0

#        print('encode: %s %s' % (img_1b_1d.shape, img_1b_1d_p.shape))
        return img_1b_1d_p

    def decode(self, img):
        """
        Decode the image from internal image format.
        """
        assert len(img.shape) == 1
        assert img.shape[0] >= (self._h * self._w / 8)
        assert img.shape[0] % self._align == 0

        img_8b_1d = np.unpackbits(img) * 255  # to 8bit gray scale.
        img_8b_1d_trimmed = img_8b_1d[0: (self._h * self._w)]
        img_8b_2d = np.reshape(img_8b_1d_trimmed, (self._h, self._w))

        return img_8b_2d

#    def convert(self, img):
#        return np.packbits(img)

    def logical_or(self, img):
        r = self._img_mask | img
        return r

    def logical_and(self, img):
        r = self._img_mask & img
        return r
