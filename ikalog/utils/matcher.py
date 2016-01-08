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

import traceback
from ikalog.utils.ikautils import *
from ikalog.utils.localization import Localization


class MM_WHITE(object):

    def evaluate_gray_image(self, img_gray):
        assert(len(img_gray.shape) == 2)

        vis_min = min(self.visibility_range)
        vis_max = max(self.visibility_range)

        assert(vis_min >= 0 and vis_max <= 256)

        img_match_v = cv2.inRange(img_gray, vis_min, vis_max)
        return img_match_v

    def evaluate(self, img_bgr=None, img_gray=None):
        if (img_bgr is None):
            return self.evaluate_gray_image(img_gray)

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
        img_match = np.minimum(img_match_s, img_match_v)
        return img_match

    def __init__(self, sat=(0, 32), visibility=(230, 256)):
        self.sat_range = sat  # assume tuple
        self.visibility_range = visibility  # assume tuple


class MM_NOT_WHITE(MM_WHITE):

    def evaluate(self, img_bgr=None, img_gray=None):
        img_result = super(MM_NOT_WHITE, self).evaluate(
            img_bgr=img_bgr, img_gray=img_gray)
        return 255 - img_result


class MM_BLACK(object):

    def evaluate(self, img_bgr=None, img_gray=None):
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


class MM_NOT_BLACK(MM_BLACK):

    def evaluate(self, img_bgr=None, img_gray=None):
        img_result = super(MM_NOT_BLACK, self).evaluate(
            img_bgr=img_bgr, img_gray=img_gray)
        return 255 - img_result

# MM_COLOR_BY_HUE:


class MM_COLOR_BY_HUE(object):

    def _hue_range_to_list(self, r):
        # FIXME: 0, 180をまたぐ場合にふたつに分ける
        return [r]

    def evaluate(self, img_bgr=None, img_gray=None):
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
            img_match = np.minimum(img_match_h, img_match_v)
        return img_match

    def __init__(self, hue=None, visibility=None):
        self.hue_range = hue  # assume tuple
        self.visibility_range = visibility  # assume tuple


class MM_NOT_COLOR_BY_HUE(MM_COLOR_BY_HUE):

    def evaluate(self, img_bgr=None, img_gray=None):
        img_result = super(MM_NOT_COLOR_BY_HUE, self).evaluate(
            img_bgr=img_bgr, img_gray=img_gray)
        return 255 - img_result


class IkaMatcher(object):

        # Match the image.
        # @param self   The object.
        # @param img    Frame data.
        # @param debug  If true, show debug information.
    def match_score(self, img, debug=None):
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

        # Check background score
        try:
            img_bg = 255 - \
                self.bg_method.evaluate(img_bgr=img_bgr, img_gray=img_gray)
            img_bg = np.minimum(img_bg, self.mask_img)
        except:
            IkaUtils.dprint('%s (%s): bg_method %s caused a exception.' % (
                self, self.label, self.bg_method.__class__.__name__))
            IkaUtils.dprint(traceback.format_exc())

        img_bg = np.minimum(img_bg, self.mask_img)

        orig_hist = cv2.calcHist([img_bg], [0], None, [3], [0, 256])
        orig_raito = (orig_hist[2] / np.sum(orig_hist))[0]

        if orig_raito > self.orig_threshold:
            raito = 0.0
            match = False
            img_added = None
            img_fg = None
        else:
            # フォアグラウンド色の一致を調べる
            img_fg = self.fg_method.evaluate(
                img_bgr=img_bgr, img_gray=img_gray)
            img_added = np.maximum(img_fg, self.mask_img)

            hist = cv2.calcHist([img_added], [0], None, [3], [0, 256])

            raito = (hist[2] / np.sum(hist))[0]
            match = (raito > self.threshold)

        if debug:  # and (match > threshold):
            label = self.label if not self.label is None else self
            print("%s: result=%s raito BG %1.3f FG %1.3f (threshold BG %1.3f FG %1.3f) label:%s" %
                  (self.__class__.__name__, match, orig_raito, raito, self.orig_threshold, self.threshold, label))
            # FIXME: 一枚の画像として表示する
            cv2.imshow('mask: %s' % label, self.mask_img)
            cv2.imshow('img_gray: %s' % label, img_gray)
            cv2.imshow('img_bg: %s' % label, img_bg)
            if img_fg is not None:
                cv2.imshow('img_fg: %s' % label, img_fg)
            if img_added is not None:
                cv2.imshow('result: %s' % label, img_added)
        return (match, raito, orig_raito)

    def match(self, img, debug=None):
        matched, fg_score, bg_score = self.match_score(img, debug)
        return matched

    def _find_image_file(self, img_file=None, languages=None):
        if languages is None:
            languages = Localization.get_game_languages()

        if languages is not None:
            if not isinstance(languages, list):
                languages = [lang]

            for lang in languages:
                f = os.path.join(IkaUtils.baseDirectory(), 'masks', lang, img_file)
                if os.path.exists(f):
                    return f

        f = os.path.join(IkaUtils.baseDirectory(), 'masks', img_file)
        if os.path.exists(f):
            return f

        f = os.path.join(IkaUtils.baseDirectory(), img_file)
        if os.path.exists(f):
            return f

        f = os.path.join(IkaUtils.baseDirectory(), 'masks', 'ja', img_file)
        if os.path.exists(f):
            IkaUtils.dprint('%s: mask %s: using ja version' %
                (self, img_file))
            return f

        raise Exception('Could not find image file %s (lang %s)' % (img_file, lang))


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
    def __init__(self, left, top, width, height, img=None, img_file=None, threshold=0.9, fg_method=None, bg_method=None, orig_threshold=0.7, debug=False, label=None):
        self.top = top
        self.left = left
        self.width = width
        self.height = height
        self.threshold = threshold
        self.orig_threshold = orig_threshold
        self.debug = debug
        self.label = label

        self.fg_method = fg_method
        if self.fg_method is None:
            self.fg_method = MM_WHITE()

        self.bg_method = bg_method
        if self.bg_method is None:
            self.bg_method = MM_NOT_WHITE()

        if not img_file is None:
            img_file2 = self._find_image_file(img_file)
            img = cv2.imread(img_file2)

            if img is None:
                IkaUtils.dprint(
                    '%s is not available. Retrying with %s' % (img_file2, img_file))
                img = cv2.imread(img_file)

        if img is None:
            raise Exception('Could not load mask image %s (%s)' %
                            (label, img_file))

        if len(img.shape) > 2 and img.shape[2] != 1:
            img = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)

        cropped = (img.shape[0] == self.height) and (
            img.shape[1] == self.width)
        if cropped:
            self.mask_img = img
        else:
            self.mask_img = img[top: top + height, left: left + width]
