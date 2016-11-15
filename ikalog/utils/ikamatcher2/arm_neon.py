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

from ctypes import c_char_p, c_double, c_int
dllfile = '/Users/hasegaw/work/IkaLog_boost/ikamatcher2_sse42.so'
ctypes.cdll.LoadLibrary(dllfile)
dll = ctypes.CDLL(dllfile)


dll.IkaMatcher2_encode.argtypes = [
    np.ctypeslib.ndpointer(dtype=np.uint8, flags='C_CONTIGUOUS'),  # dest
    np.ctypeslib.ndpointer(dtype=np.uint8, flags='C_CONTIGUOUS'),  # src
    c_int,  # pixels
]
dll.IkaMatcher2_encode.restype = c_int

dll.IkaMatcher2_popcnt128.argtypes = [
    np.ctypeslib.ndpointer(dtype=np.uint8, flags='C_CONTIGUOUS'),  # src
    c_int,  # pixels
]
dll.IkaMatcher2_popcnt128.restype = c_int

dll.gray2binary.argtypes = [
    np.ctypeslib.ndpointer(dtype=np.uint8, flags='C_CONTIGUOUS'),  # src
    np.ctypeslib.ndpointer(dtype=np.uint8, flags='C_CONTIGUOUS'),  # dest
    c_int,  # pixels
]
dll.gray2binary.restype = c_int


class ARM_NEON(NumpyBit):

    def encode(self, img):
        """
        Encode the image to internal image format.

        Bits per pixel:               1bit (uint8)
        Alignment per lines:         0
        Alignment of returned image: self._align bytes
        """

        width = 128

        assert img.shape[0] == self._h
        assert img.shape[1] == self._w

        img_8b_1d = np.reshape(img, (-1))

        padding_len = width - (img_8b_1d.shape[0] % width)
        if padding_len:
            img_8b_1d_p = np.append(img_8b_1d, self.zeros128[0: padding_len])
        else:
            img_8b_1d_p = img_8b_1d

        assert len(img_8b_1d_p.shape) == 1
        assert img_8b_1d_p.shape[0] >= (self._h * self._w / 8)
        assert img_8b_1d_p.shape[0] % self._align == 0

        dest = np.zeros(int(img_8b_1d_p.shape[0]) / 8, dtype=np.uint8)
        dest_pixels = dll.gray2binary(img_8b_1d_p, dest, img_8b_1d_p.shape[0])

        assert dest_pixels <= dest.shape[0]

        return dest

    def decode(self, img):
        return decode_1bit(self, img)
