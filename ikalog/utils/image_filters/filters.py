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
import numpy as np

from ikalog.utils import IkaUtils

class ImageFilter(object):

    want_grayscale_image = True
    
    # For backward compatibility
    _warned_evaluate_is_deprecated = False

    def evaluate(self, img_bgr=None, img_gray=None):
        # if not hasattr(self, '_warned_evaluate_is_deprecated'):

        if not self._warned_evaluate_is_deprecated:

            IkaUtils.dprint('%s: evaluate() is depricated.' % self)
            self._warned_evaluate_is_deprecated = True

        return self(img_bgr=img_bgr, img_gray=img_gray)

    def _run_filter(self, img_bgr=None, img_gray=None):
        raise Exception('Need to be overrided')

    def __call__(self, img_bgr=None, img_gray=None):
        return self._run_filter(img_bgr=img_bgr, img_gray=img_gray)


class MM_WHITE(ImageFilter):

    def _run_filter_gray_image(self, img_gray):
        assert(len(img_gray.shape) == 2)

        vis_min = min(self.visibility_range)
        vis_max = max(self.visibility_range)

        assert(vis_min >= 0 and vis_max <= 256)

        img_match_v = cv2.inRange(img_gray, vis_min, vis_max)
        return img_match_v

    def _run_filter(self, img_bgr=None, img_gray=None):
        if (img_bgr is None):
            return self._run_filter_gray_image(img_gray)

        # カラー画像から白い部分だけ抜き出した白黒画像を作る

        assert(len(img_bgr.shape) == 3)
        assert(img_bgr.shape[2] == 3)

        sat_min = min(self.sat_range)
        sat_max = max(self.sat_range)
        vis_min = min(self.visibility_range)
        vis_max = max(self.visibility_range)

        assert(sat_min >= 0 and sat_max <= 256)
        assert(vis_min >= 0 and vis_max <= 256)

        img_hsv = cv2.cvtColor(img_bgr, cv2.COLOR_BGR2HSV)
        img_match_s = cv2.inRange(img_hsv[:, :, 1], sat_min, sat_max)
        img_match_v = cv2.inRange(img_hsv[:, :, 2], vis_min, vis_max)
        img_match = img_match_s & img_match_v
        return img_match

    def __init__(self, sat=(0, 32), visibility=(230, 256)):
        self.sat_range = sat  # assume tuple
        self.visibility_range = visibility  # assume tuple


class MM_NOT_WHITE(MM_WHITE):

    def _run_filter(self, img_bgr=None, img_gray=None):
        img_result = super(MM_NOT_WHITE, self)._run_filter(
            img_bgr=img_bgr, img_gray=img_gray)
        return 255 - img_result


class MM_BLACK(ImageFilter):

    def _run_filter(self, img_bgr=None, img_gray=None):
        assert((img_bgr is not None) or (img_gray is not None))

        if (img_gray is None):
            assert(len(img_bgr.shape) == 3)
            assert(img_bgr.shape[2] == 3)
            img_gray = cv2.cvtColor(img_bgr, cv2.COLOR_BGR2GRAY)

        vis_min = min(self.visibility_range)
        vis_max = max(self.visibility_range)

        assert(vis_min >= 0 and vis_max <= 256)
        img_match_v = cv2.inRange(img_gray[:, :], vis_min, vis_max)
        return img_match_v

    def __init__(self, visibility=(0, 32)):
        self.visibility_range = visibility


class MM_DARK(MM_BLACK):

    def __init__(self, visibility=(0, 64)):
        super(MM_DARK, self).__init__(visibility=visibility)

class MM_NOT_DARK(MM_BLACK):
    def __init__(self, visibility=(64, 255)):
        super(MM_NOT_DARK, self).__init__(visibility=visibility)

class MM_NOT_BLACK(MM_BLACK):

    def _run_filter(self, img_bgr=None, img_gray=None):
        img_result = super(MM_NOT_BLACK, self)._run_filter(
            img_bgr=img_bgr, img_gray=img_gray)
        return 255 - img_result


class MM_COLOR_BY_HUE(ImageFilter):

    want_grayscale_image = False

    def _hue_range_to_list(self, r):
        # FIXME: 0, 180をまたぐ場合にふたつに分ける
        return [r]

    def _run_filter(self, img_bgr=None, img_gray=None):
        assert(img_bgr is not None)
        assert(len(img_bgr.shape) >= 3)
        assert(img_bgr.shape[2] == 3)
        assert(len(self._hue_range_to_list(self.hue_range)) == 1)  # FIXME

        img_hsv = cv2.cvtColor(img_bgr, cv2.COLOR_BGR2HSV)

        vis_min = min(self.visibility_range)
        vis_max = max(self.visibility_range)

        assert(vis_min >= 0)
        assert(vis_max <= 256)

        for hue_range in self._hue_range_to_list(self.hue_range):
            hue_min = min(self.hue_range)
            hue_max = max(self.hue_range)

            assert(hue_min >= 0)
            assert(hue_max <= 256)

            #print('vis_min %d vis_max %d hue_min %d hue_max %d' % (vis_min, vis_max, hue_min, hue_max))
            img_match_h = cv2.inRange(img_hsv[:, :, 0], hue_min, hue_max)
            img_match_v = cv2.inRange(img_hsv[:, :, 2], vis_min, vis_max)
            img_match = img_match_h & img_match_v
        return img_match

    def __init__(self, hue=None, visibility=None):
        self.hue_range = hue  # assume tuple
        self.visibility_range = visibility  # assume tuple


class MM_NOT_COLOR_BY_HUE(MM_COLOR_BY_HUE):

    want_grayscale_image = False

    def _run_filter(self, img_bgr=None, img_gray=None):
        img_result = super(MM_NOT_COLOR_BY_HUE, self)._run_filter(
            img_bgr=img_bgr, img_gray=img_gray)
        return 255 - img_result

