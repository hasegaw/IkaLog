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
from ikalog.utils.ikautils import *

# Match images with mask data.
class IkaMatcher(object):

    # Calculate false-postive score (masked area must be black)
    @classmethod
    def FP_BACK_IS_BLACK(cls, mask_img=None, img_bgr=None, img_gray=None):
        fp_img = np.minimum(img_gray, mask_img)
        fp_img = cv2.inRange(fp_img, 16, 256)
        orig_hist = cv2.calcHist([fp_img], [0], None, [3], [0, 256])
        orig_raito = orig_hist[2] / np.sum(orig_hist)
        return orig_raito, fp_img

    # Calculate false-postive score (masked area is not white)
    @classmethod
    def FP_FRONT_IS_WHITE(cls, mask_img=None, img_bgr=None, img_gray=None):
        img_hsv = cv2.cvtColor(img_bgr, cv2.COLOR_BGR2HSV)
        white_mask_s = cv2.inRange(img_hsv[:, :, 1], 0, 6)
        white_mask_v = cv2.inRange(img_hsv[:, :, 2], 250, 256)
        # マスク範囲=0, 白以外=0, 白=255
        fp_img = np.minimum(mask_img, white_mask_s, white_mask_v)
        orig_hist = cv2.calcHist([fp_img], [0], None, [3], [0, 256])
        orig_raito = orig_hist[2] / np.sum(orig_hist)
        return orig_raito, fp_img

    # Match the image.
    # @param self   The object.
    # @param img    Frame data.
    # @param debug  If true, show debug information.
    def match(self, img, debug=None):
        if debug is None:
            debug = self.debug

        # Crop
        cropped = (img.shape[0] == self.height) and (
            img.shape[1] == self.width)
        if not cropped:
            img = img[self.top: self.top + self.height,
                      self.left: self.left + self.width]

        # Grayscale
        if len(img.shape) > 2:
            img_bgr = img
            img_gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
        else:
            img_bgr = None
            img_gray = img

        # Check false-positive
        #orig_raito  = self.FP_BACK_IS_BLACK(img_gray = img)
        orig_raito, img_fp = self.false_positive_method(
            mask_img=self.mask_img, img_bgr=img_bgr, img_gray=img_gray)
        raito = 0

        match = True

        if orig_raito > self.orig_threshold:
            match = False
            if debug:
                pass
                #print("original image exceeded orig_threshold")

        if match and not (self.pre_threshold_value is None):
            ret, img_gray = cv2.threshold(
                img_gray, self.pre_threshold_value, 255, cv2.THRESH_BINARY)

        if match:
            added = np.maximum(img_gray, self.mask_img)

            hist = cv2.calcHist([added], [0], None, [3], [0, 256])

            raito = hist[2] / np.sum(hist)
            match = raito > self.threshold
        else:
            added = None

        if debug:  # and (match > threshold):
            label = self.label if not self.label is None else self
            print("%s(%s): result=%s raito %f orig_raito %f, threshold %3.3f orig_threshold %3.3f" %
                  (self.__class__.__name__, label, match, raito, orig_raito, self.threshold, self.orig_threshold))
            cv2.imshow('img_fp: %s' % label, img_fp)
            cv2.imshow('img_gray: %s' % label, img_gray)
            cv2.imshow('mask: %s' % label, self.mask_img)
            if not added is None:
                cv2.imshow('result: %s' % label, added)

        return match

    # Constructor.
    # @param self                 The object.
    # @param left                 Left of the mask.
    # @param top                  Top of the mask.
    # @param width                Width of the mask.
    # @param height               Height of the mask.
    # @param img                  Instance of the mask image.
    # @param img_file             Filename of the mask image.
    # @param threshold            Threshold
    # @param orig_threshold       Target frame must be lower than this raito.
    # @prram pre_threshold_value  Threshold target frame with this level before matching.
    # @param debug                If true, show debug information.
    # @param label                Label (text data) to distingish this mask.
    def __init__(self, left, top, width, height, img=None, img_file=None, threshold=0.9, false_positive_method=None, orig_threshold=0.7, pre_threshold_value=230, debug=False, label=None):
        self.top = top
        self.left = left
        self.width = width
        self.height = height
        self.threshold = threshold
        self.orig_threshold = orig_threshold
        self.pre_threshold_value = pre_threshold_value
        self.debug = debug
        self.label = label
        self.false_positive_method = false_positive_method if not false_positive_method is None else IkaMatcher.FP_FRONT_IS_WHITE

        if not img_file is None:
            img_file2 = os.path.join(IkaUtils.baseDirectory(), img_file)
            img = cv2.imread(img_file2)

            if img is None:
                IkaUtils.dprint('%s is not available. Retrying with %s' % (img_file2, img_file))
                img = cv2.imread(img_file)

        if img is None:
            raise Exception('Could not load mask image %s (%s)' % (label, img_file))

        if len(img.shape) > 2 and img.shape[2] != 1:
            img = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)

        cropped = (img.shape[0] == self.height) and (
            img.shape[1] == self.width)
        if cropped:
            self.mask_img = img
        else:
            self.mask_img = img[top: top + height, left: left + width]
