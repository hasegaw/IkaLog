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

import copy
import cv2
import numpy as np


class Kernel(object):

    def __init__(self, w, h):
        """
        Constructor
        """
        self._w = w
        self._h = h

    def encode(self, img):
        """
        Encode the image to kenrel-preferred format.

        Args:
            img: The image to encode.
        Returns:
            The encoded data
        """
        raise Exception("This function should be overrided")

    def decode(self, img):
        """
        Decode the the kenrel-preferred format to BGR image.

        Args:
            img: The image to encode.
        Returns:
            The encoded data
        """
        raise Exception("This function should be overrided")

    def popcnt(self, img_kernel):
        """
        Count white pixels in the image.

        Args:
            img: The image to perform popcnt.
        Returns:
            Number of white pixels
        """
        raise Exception("This function should be overrided")
    
    def logical_or(self, img=None):
        """
        Logical OR implementation.
        Any implemention mustoverride this method.

        1) Perform OR operation.

        Truth table (A OR B)
        | Mask | Image | Expected Result |
        |   0  |     0 |               0 |
        |   0  |   255 |             255 |
        |  255 |     0 |             255 |
        |  255 |   255 |             255 |

        Args:
            img: the image to perform OR with the mask

        Returns:
            The result image
        """
        raise Exception("This function should be overrided")

    def logical_and(self, img=None):
        """
        Logical AND implementation.
        Any implemention mustoverride this method.

        Truth table (A AND B)
        | Mask | Image | Expected Result |
        |   0  |     0 |               0 |
        |   0  |   255 |               0 |
        |  255 |     0 |               0 |
        |  255 |   255 |             255 |

        Args:
            img: the image to perform AND with the mask

        Returns:
            The result image
        """
        raise Exception("This function should be overrided")

    def logical_and_popcnt(self, img):
        img_result_kernel = self.logical_and(img)
        return self.popcnt(img_result_kernel)

    def logical_or_popcnt(self, img):
        img_result_kernel = self.logical_or(img)
        return self.popcnt(img_result_kernel)

    def load_mask(self, img_mask):
        """
        load_mask receives and hold the mask image.

        Args:
            img_mask: mask image (BGR 8bit format)
        """
        assert len(img_mask.shape) == 2
        assert img_mask.shape[0] == self._h
        assert img_mask.shape[1] == self._w

        # IkaMatcher2 compatibilty
        img_mask = copy.deepcopy(img_mask)
        img_mask[img_mask < 170] = 0
        img_mask[img_mask > 0] = 255

        self._img_mask = self.encode(img_mask)
