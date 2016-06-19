#!/usr/bin/env python3
# -*- coding: utf-8 -*-
#
#  IkaLog
#  ======
#  Copyright (C) 2016 Takeshi HASEGAWA
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

from ikalog.utils import matcher

_TRUTH_2_SVM = {True: 1, False: -1}
_SVM_2_ZEROONE = {-1: 0, 1: 1}


def normalize_player_name(img_name, debug=False):
    img_name_w_norm = np.zeros((15, 250), dtype=np.uint8)
    img_name_w = matcher.MM_WHITE(sat=(0, 96), visibility=(48, 255))(img_name)

    img_name_x_hist = np.extract(
        np.sum(img_name_w, axis=0) > 128,
        np.arange(img_name_w.shape[1]),
    )

    img_name_y_hist = np.extract(
        np.sum(img_name_w, axis=1) > 128,
        np.arange(img_name_w.shape[0]),
    )

    if (len(img_name_x_hist) == 0) or (len(img_name_y_hist) == 0):
        # In some cases, we can't find any pixels.
        return img_name_w_norm

    img_name_left = np.min(img_name_x_hist)
    img_name_right = np.max(img_name_x_hist)

    img_name_top = np.min(img_name_y_hist)
    img_name_bottom = np.max(img_name_y_hist)

    # Cropping error? should be handled gracefully.
    if not (img_name_left < img_name_right):
        return None

    img_name_w = img_name_w[
        img_name_top:img_name_bottom, img_name_left:img_name_right]

    img_name_w_norm[:, 0: img_name_w.shape[1]] = cv2.resize(
        img_name_w, (img_name_w.shape[1], 15))

    if debug:
        print(img_name_w_norm.shape)
        cv2.imshow('name', img_name_w_norm)
        cv2.waitKey(1)

    return img_name_w_norm


def train_svm_classifiers(img_name_list, debug=False):
    """
    Train player name classifier for specified img_name list.

    The images will be training with OpenCV Support Vector Machine functions.
    Returns list of SVM objects.

    The array would have "None" for the entry that SVM was not properly
    trained.
    """
    assert isinstance(img_name_list, list)

    img_name_list = np.array(img_name_list, dtype=np.float32)

    X = np.array(
        list(map(lambda img: np.array(img).reshape((-1)), img_name_list)))

    # Train SVM per counter player.
    H = []
    for img in img_name_list:
        # y = Response for SVM Training. e.g. [1, -1, -1, -1]
        y = list(map(lambda e: _TRUTH_2_SVM[
                 np.array_equal(e, img)], img_name_list))
        y = np.array(y, dtype=np.int)

        h = cv2.ml.SVM_create()
        h.setGamma(1)
        h.setC(1)
        h.setKernel(cv2.ml.SVM_LINEAR)
        h.setType(cv2.ml.SVM_C_SVC)

        h.train(X, cv2.ml.ROW_SAMPLE, y)

        # Test the model.
        r, predicted = h.predict(X)
        predicted_01 = None
        if r == 0:
            predicted_01 = map(lambda e: _SVM_2_ZEROONE[int(e)], predicted)
            predicted_01 = list(predicted_01)
            ok = (np.sum(predicted_01) == 1) and \
                (np.argmax(y) == np.argmax(predicted_01))

            if not ok:
                h = None

        else:
            # SVM Classification failed.
            h = None

        H.append(h)

    print(H)
    import time
    time.sleep(3)
    return H


def predict(self, H_list, img_name):
    """
    Predict the specified image.

    Returns index number, or None if it is not certain.
    """

    features = np.array(img_name, dtype=np.float32).reshape((1, -1))

    matched = 0
    index = None

    for h in H_list:
        # Skip invalid hypothesises.
        if h is None:
            continue

        r, predicted = h.predict(features)
        if predicted[0] > 0:
            matched = matched + 1
            index = H_list.index(h)

    # If there are more than two or no matches, return None.
    if matched != 1:
        return None

    # If there is the exact match, return the index.
    return index


class PlayerNameClassifier(object):

    def __init__(self, img_name_list, debug=False):
        self._models = train_svm_classifiers(img_name_list, debug=debug)

    def predict(self, img_name, debug=False):
        """
        Predict the specified image.

        Returns index number, or None if it is not certain.
        """

        return predict(self, self._models, img_name)
