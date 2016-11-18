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

import cv2
import numpy as np
import traceback

from ikalog.utils.find_image_file import find_image_file
from ikalog.utils.ikautils import IkaUtils
from ikalog.utils.image_filters.filters import *

from ikalog.utils.ikamatcher2.reference import Numpy_uint8_fast

default_kernel = Numpy_uint8_fast


class IkaMatcher2(object):

    zeros128 = np.array([0] * 128, dtype=np.uint8)

    def _is_cropped(self, img):
        """
        Check the image size and check if the image is already cropped.
        """
        cropped = \
            (img.shape[0] == self._height) and \
            (img.shape[1] == self._width)
        return cropped

    def get_img_object(self, img):
        if not self._is_cropped(img):
            img = img[self._top: self._top + self._height,
                      self._left: self._left + self._width]

        if len(img.shape) == 2:
            img_gray = img
            img_bgr = None
        else:
            img_gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
            img_bgr = img

        return { 'bgr': img_bgr, 'gray': img_gray, 'bg': None, 'fg': None }

    def match(self, img, debug=None):
        matched, fg_score, bg_score = self.match_score(img, debug)
        return matched

    def match_score(self, img, debug=None):
        img_obj = self.get_img_object(img)
        return self.match_score_internal(img_obj, debug=debug)

    def match_score_internal(self, img_obj, debug=None):
        debug = debug or self._debug

        bg_pixels = 0
        bg_ratio = 0.0
        bg_matched = False

        fg_pixels = 0
        fg_ratio = 0.0
        fg_matched = False

        # Phase 2: Background check
        try:
            if img_obj['bg'] is None:
                img_bg = 255 - \
                    self._bg_method(img_bgr=img_obj['bgr'], img_gray=img_obj['gray'])
                img_obj['bg'] = self._kernel.encode(img_bg)
            bg_pixels = self._kernel.logical_and_popcnt(img_obj['bg'])

            # fixme: zero division
            bg_ratio = bg_pixels / (self._width * self._height)
            bg_matched = (bg_ratio <= self._orig_threshold)
        except:
            IkaUtils.dprint('%s (%s): bg_method %s caused a exception.' % (
                self, self._label, self._bg_method.__class__.__name__))
            IkaUtils.dprint(traceback.format_exc())

        # Phase 3: Foreground check
        if bg_matched:
            if img_obj['fg'] is None:
                img_fg = self._fg_method(img_bgr=img_obj['bgr'], img_gray=img_obj['gray'])
                img_obj['fg'] = self._kernel.encode(img_fg)
            fg_pixels = self._kernel.logical_or_popcnt(img_obj['fg'])

            # fixme: zero division
            fg_ratio = fg_pixels / (self._width * self._height)
            fg_matched = (fg_ratio > self._threshold)

        if debug:
            label = self._label
            print("%s: result=%s raito BG %s FG %s (threshold BG %1.3f FG %1.3f) label:%s" %
                  (self.__class__.__name__, fg_matched, bg_ratio, fg_ratio,
                   self._orig_threshold, self._threshold, label))
        # ToDo: imshow

        # ToDo: on_mark_rect_in_preview

        return (fg_matched, fg_ratio, bg_ratio)

    def __init__(self, left, top, width, height, img=None, img_file=None, threshold=0.9, fg_method=None, bg_method=None, orig_threshold=0.7, debug=False, label=None, call_plugins=None, kernel_class=None):
        """
        Constructor

        Args:
            self                 The object.
            left                 Left of the mask.
            top                  Top of the mask.
            width                Width of the mask.
            height               Height of the mask.
            img                  Instance of the mask image.
            img_file             Filename of the mask image.
            threshold            Threshold
            orig_threshold       Target frame must be lower than this raito.
            pre_threshold_value  Threshold target frame with this level before matching.
            debug                If true, show debug information.
            label                Label (text data) to distingish this mask.
        """
        self._top = top
        self._left = left
        self._width = width
        self._height = height
        self._threshold = threshold
        self._orig_threshold = orig_threshold
        self._debug = debug
        self._label = label
        self._call_plugins = call_plugins

        self._fg_method = fg_method or MM_WHITE()
        self._bg_method = bg_method or MM_NOT_WHITE()
        if not img_file is None:
            img_file2 = find_image_file(img_file)
            img = cv2.imread(img_file2)  # FIXME: use own imread

            if img is None:
                IkaUtils.dprint(
                    '%s is not available. Retrying with %s' % (img_file2, img_file))
                img = cv2.imread(img_file)  # FIXME

        if img is None:
            raise Exception('Could not load mask image %s (%s)' %
                            (label, img_file))

        if len(img.shape) > 2 and img.shape[2] != 1:
            img = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)

        if not self._is_cropped(img):
            img = img[top: top + height, left: left + width]

        # Initialize kernel
        kernel_class = kernel_class or default_kernel
        self._kernel = kernel_class(self._width, self._height)
        self._kernel.load_mask(img)
