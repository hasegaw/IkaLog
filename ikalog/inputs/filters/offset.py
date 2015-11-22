#!/usr/bin/env python3
# -*- coding: utf-8 -*-
#
#  IkaLog
#  ======
#  Copyright (C) 2015 Hiromichi Itou
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

#
#  This source includes modified version of sample codes in OpenCV
#  distribution, licensed under 3-clause BSD License.
#
# By downloading, copying, installing or using the software you agree to this license.
# If you do not agree to this license, do not download, install,
# copy or use the software.
#
#
#                           License Agreement
#                For Open Source Computer Vision Library
#                        (3-clause BSD License)
#
# Copyright (C) 2000-2015, Intel Corporation, all rights reserved.
# Copyright (C) 2009-2011, Willow Garage Inc., all rights reserved.
# Copyright (C) 2009-2015, NVIDIA Corporation, all rights reserved.
# Copyright (C) 2010-2013, Advanced Micro Devices, Inc., all rights reserved.
# Copyright (C) 2015, OpenCV Foundation, all rights reserved.
# Copyright (C) 2015, Itseez Inc., all rights reserved.
# Third party copyrights are property of their respective owners.
#
# Redistribution and use in source and binary forms, with or without modification,
# are permitted provided that the following conditions are met:
#
#   * Redistributions of source code must retain the above copyright notice,
#     this list of conditions and the following disclaimer.
#
#   * Redistributions in binary form must reproduce the above copyright notice,
#     this list of conditions and the following disclaimer in the documentation
#     and/or other materials provided with the distribution.
#
#   * Neither the names of the copyright holders nor the names of the contributors
#     may be used to endorse or promote products derived from this software
#     without specific prior written permission.
#
# This software is provided by the copyright holders and contributors "as is" and
# any express or implied warranties, including, but not limited to, the implied
# warranties of merchantability and fitness for a particular purpose are disclaimed.
# In no event shall copyright holders or contributors be liable for any direct,
# indirect, incidental, special, exemplary, or consequential damages
# (including, but not limited to, procurement of substitute goods or services;
# loss of use, data, or profits; or business interruption) however caused
# and on any theory of liability, whether in contract, strict liability,
# or tort (including negligence or otherwise) arising in any way out of
# the use of this software, even if advised of the possibility of such damage.
#

import os
import pickle

import cv2
import numpy as np

from ikalog.inputs.filters import Filter, WarpFilterModel
from ikalog.utils import *


class OffsetFilter(Filter):

    def filter_matches(self, kp1, kp2, matches, ratio=0.75):
        mkp1, mkp2 = [], []
        for m in matches:
            if len(m) == 2 and m[0].distance < m[1].distance * ratio:
                m = m[0]
                mkp1.append(kp1[m.queryIdx])
                mkp2.append(kp2[m.trainIdx])
        p1 = np.float32([kp.pt for kp in mkp1])
        p2 = np.float32([kp.pt for kp in mkp2])
        kp_pairs = zip(mkp1, mkp2)
        return p1, p2, kp_pairs

    def calibrateWarp(self, capture_image):
        capture_image_gray = cv2.cvtColor(capture_image, cv2.COLOR_BGR2GRAY)

        capture_image_keypoints, capture_image_descriptors = self.detector.detectAndCompute(
            capture_image_gray, None)
        print('caputure_image - %d features' % (len(capture_image_keypoints)))

        print('matching...')

        raw_matches = self.matcher.knnMatch(
            self.calibration_image_descriptors,
            trainDescriptors=capture_image_descriptors,
            k=2
        )
        p1, p2, kp_pairs = self.filter_matches(
            self.calibration_image_keypoints,
            capture_image_keypoints,
            raw_matches,
        )

        if len(p1) >= 4:
            H, status = cv2.findHomography(p1, p2, cv2.RANSAC, 5.0)
            print('%d / %d  inliers/matched' % (np.sum(status), len(status)))
        else:
            H, status = None, None
            print('%d matches found, not enough for homography estimation' % len(p1))
            self.calibration_requested = False
            return False

        if H is None:
            # Should never reach there...
            self.calibration_requested = False
            return False

        calibration_image_height, calibration_image_width = self.calibration_image_size

        corners = np.float32(
            [[0, 0],
             [calibration_image_width, 0],
             [calibration_image_width, calibration_image_height],
             [0, calibration_image_height]]
        )

        pts1 = np.float32(cv2.perspectiveTransform(
            corners.reshape(1, -1, 2), H).reshape(-1, 2) + (0, 0))

        IkaUtils.dprint('pts1: %s' % [pts1])
        IkaUtils.dprint('pts2: %s' % [self.pts2])

        offset_average = np.average([pts1 - self.pts2],axis=1)
        offset_around = np.around([offset_average]).astype(np.int32)
        self.offset = offset_around[0][0]

        IkaUtils.dprint('offset: %s' % [self.offset])

        return True

    def initializeCalibration(self):
        model_object = WarpFilterModel()

        if not model_object.trained:
            raise Exception('Could not intialize WarpFilterModel')

        self.detector = model_object.detector
        self.norm = model_object.norm
        self.matcher = model_object.matcher

        self.calibration_image_size = model_object.calibration_image_size
        self.calibration_image_keypoints = model_object.calibration_image_keypoints
        self.calibration_image_descriptors = model_object.calibration_image_descriptors

        self.reset()

    def reset(self):
        # input source
        w = 1280
        h = 720

        self.pts2 = np.float32([[0, 0], [w, 0], [w, h], [0, h]])
        self.offset = (0, 0)

    def pre_execute(self, frame):
        return True

    def execute(self, frame):
        if not (self.enabled and self.pre_execute(frame)):
            return frame

        ox = self.offset[0]
        oy = self.offset[1]

        sx1 = max(-ox, 0)
        sy1 = max(-oy, 0)

        dx1 = max(ox, 0)
        dy1 = max(oy, 0)

        out_width = self.parent.out_width
        out_height = self.parent.out_height

        w = min(out_width - dx1, out_width - sx1)
        h = min(out_height - dy1, out_height - sy1)

        new_frame = np.zeros((out_height, out_width, 3), np.uint8)
        new_frame[dy1:dy1 + h, dx1:dx1 + w] = frame[sy1:sy1 + h, sx1:sx1 + w]
        return new_frame

    def __init__(self, parent, debug=False):
        super().__init__(parent, debug=debug)
        self.initializeCalibration()
