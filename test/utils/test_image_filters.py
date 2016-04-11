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

#  Unit test for ikautils.
#  Usage:
#    python ./test_ikautils.py
#  or
#    py.test ./test_ikautils.py

import os
import sys
import unittest

import numpy as np
import cv2

# Append the Ikalog root dir to sys.path to import IkaUtils.
sys.path.append(os.path.join(os.path.dirname(__file__), '..', '..'))
from ikalog.utils.image_filters import *


class TestImageFilters(unittest.TestCase):

    def test_MM_WHITE(self):
        img1 = np.zeros((100, 100, 3), dtype=np.uint8)

        cv2.rectangle(img1, (10, 10), (90, 90), (255, 255, 255), 3)
        img2 = MM_WHITE()(img1)

        img_diff = np.array(img1[:, :, 0], dtype=int) - \
            np.array(img2, dtype=int)
        assert np.max(np.abs(img_diff)) == 0

    def test_MM_NOT_WHITE(self):
        img1 = np.zeros((100, 100, 3), dtype=np.uint8)

        cv2.rectangle(img1, (10, 10), (90, 90), (255, 255, 255), 3)
        img2 = MM_NOT_WHITE()(img1)

        img_diff = np.array(255 - img1[:, :, 0], dtype=int) - \
            np.array(img2, dtype=int)
        assert np.max(np.abs(img_diff)) == 0

    def test_MM_COLOR_BY_HUE(self):
        img1 = np.zeros((100, 100, 3), dtype=np.uint8)

        cv2.rectangle(img1, (10, 10), (90, 90), (255, 0, 0), 3)
        img2 = MM_COLOR_BY_HUE(hue=(120 - 5, 120 + 5),
                               visibility=(0, 255))(img1)

        cv2.imshow('a', img1)
        cv2.imshow('b', img2)
        cv2.waitKey()

        img_diff = np.array(img1[:, :, 0], dtype=int) - \
            np.array(img2, dtype=int)
        assert np.max(np.abs(img_diff)) == 0

    def test_MM_DARK(self):
        img1 = np.zeros((100, 100, 3), dtype=np.uint8)

        cv2.rectangle(img1, (10, 10), (90, 90), (255, 255, 255), 3)
        img2 = MM_DARK()(img1)

        img_diff = np.array(255 - img1[:, :, 0], dtype=int) - \
            np.array(img2, dtype=int)
        assert np.max(np.abs(img_diff)) == 0

    def test_MM_BLACK(self):
        img1 = np.zeros((100, 100, 3), dtype=np.uint8)

        cv2.rectangle(img1, (10, 10), (90, 90), (255, 255, 255), 3)
        img2 = MM_BLACK()(img1)

        img_diff = np.array(255 - img1[:, :, 0], dtype=int) - \
            np.array(img2, dtype=int)
        assert np.max(np.abs(img_diff)) == 0

    def test_MM_NOT_COLOR_BY_HUE(self):
        img1 = np.zeros((100, 100, 3), dtype=np.uint8)

        cv2.rectangle(img1, (10, 10), (90, 90), (255, 0, 0), 3)
        img2 = MM_NOT_COLOR_BY_HUE(
            hue=(120 - 5, 120 + 5), visibility=(100, 255))(img1)

        img_diff = np.array(255 - img1[:, :, 0], dtype=int) - \
            np.array(img2, dtype=int)
        assert np.max(np.abs(img_diff)) == 0
