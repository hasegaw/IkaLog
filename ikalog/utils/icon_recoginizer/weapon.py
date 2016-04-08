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

import cv2
import numpy as np

from ikalog.utils.icon_recoginizer import IconRecoginizer


def get_img_custom(self, img):
    (h, w) = img.shape[0:2]
    return img[int(h * 0.7):, int(w * 0.7):]


def max_pooling_2d(self, img, xy=(2, 2)):
    x, y = xy
    oh, ow = img.shape
    hw = int(ow / x)
    hh = int(oh / y)
    img = img[:hh * y, :hw * x]
    oh, ow = img.shape

    img_360p = np.max(img.reshape((oh, hw, x)),
                      axis=2).T.reshape((hw, hh, y))
    img_360p = np.max(img_360p, axis=2).T
    return img_360p


def sub_average(img):
    img_f = np.asarray(img, dtype=np.float32)
    for i in range(img_f.shape[2]):
        avg = np.average(img_f[:, :, i])
        img_f[:, :, i] = (img_f[:, :, i] - avg)
        img_f[:, :, i] = img_f[:, :, i] - np.amin(img_f[:, :, i])
        img_f[:, :, i] = img_f[:, :, i] / np.amax(img_f[:, :, i])

    img2 = np.asarray(img_f, dtype=np.uint8)
    return img2


class WeaponRecoginizer(IconRecoginizer):

    def extract_main_features(self, img, debug=False):
        h, w = img.shape[0:2]
        img_cropped = img[2:h - 4, 10:w - 3]

        img_normalized = self.normalize_icon_image(img_cropped)
        return img_normalized[0]

    def extract_sub_features(self, img, debug=False):
        laplacian_threshold = 192
        img_subavg = sub_average(img)
        img_gray = cv2.cvtColor(img_subavg, cv2.COLOR_BGR2GRAY)
        img_gray_laplacian = cv2.Laplacian(img_gray, cv2.CV_64F)
        img_laplacian_abs = cv2.convertScaleAbs(img_gray_laplacian)
        a, img_laplacian_abs_thres = cv2.threshold(
            img_laplacian_abs, laplacian_threshold, 255, 0)

        img_gray_custom = get_img_custom(None, img_gray)
        img_gray_custom = max_pooling_2d(None, img_gray, (4, 4))
        return np.array(img_gray_custom, dtype=np.float32)

    # Define weapon classification specific features.
    def extract_features_func(self, img, debug=False):
        features_main = self.extract_main_features(img)
        features_sub = self.extract_sub_features(img)
        features = np.append(
            features_main.reshape(-1),
            features_sub.reshape(-1),
        )
        return features

    def model_filename(self):
        return 'data/weapons.knn.data'

    def load_model_from_file(self, model_file=None):
        if model_file is None:
            model_file = self.model_filename()

        super(WeaponRecoginizer, self).load_model_from_file(model_file)

    def save_model_to_file(self, model_file=None):
        if model_file is None:
            model_file = self.model_filename()

        super(WeaponRecoginizer, self).save_model_to_file(model_file)

    def __new__(cls, *args, **kwargs):

        if not hasattr(cls, '__instance__'):
            cls.__instance__ = super(
                WeaponRecoginizer, cls).__new__(cls, *args, **kwargs)

        return cls.__instance__

    def __init__(self, model_file=None):

        if hasattr(self, 'trained') and self.trained:
            return

        super(WeaponRecoginizer, self).__init__(k=5)
