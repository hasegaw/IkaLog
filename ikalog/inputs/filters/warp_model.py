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

from ikalog.utils import *

class WarpFilterModel(object):

    def tuples2keyPoints(self, tuples):
        new_l = []
        for point in tuples:
            pt, size, angle, response, octave, class_id = point
            new_l.append(cv2.KeyPoint(
                pt[0], pt[1], size, angle, response, octave, class_id))
        return new_l

    def keyPoints2tuples(self, points):
        new_l = []
        for point in points:
            new_l.append((point.pt, point.size, point.angle, point.response, point.octave,
                          point.class_id))
        return new_l

    def loadModelFromFile(self, file):
        f = open(file, 'rb')
        l = pickle.load(f)
        f.close()
        self.calibration_image_size = l[0]
        self.calibration_image_keypoints = self.tuples2keyPoints(l[1])
        self.calibration_image_descriptors = l[2]

    def saveModelToFile(self, file):
        f = open(file, 'wb')
        pickle.dump([
            self.calibration_image_size,
            self.keyPoints2tuples(self.calibration_image_keypoints),
            self.calibration_image_descriptors,
        ], f)
        f.close()

    def __new__(cls, *args, **kwargs):

        if not hasattr(cls, '__instance__'):
            cls.__instance__ = super(
                WarpFilterModel, cls).__new__(cls, *args, **kwargs)

        return cls.__instance__

    def __init__(self):

        if hasattr(self, 'trained') and self.trained:
            return

        super(WarpFilterModel, self).__init__()

        model_filename = os.path.join(
            IkaUtils.baseDirectory(), 'data', 'webcam_calibration.model')
        # print(model_filename)

        self.detector = cv2.AKAZE_create()
        self.norm = cv2.NORM_HAMMING
        self.matcher = cv2.BFMatcher(self.norm)

        try:
            self.loadModelFromFile(model_filename)
            num_keypoints = len(self.calibration_image_keypoints)
            IkaUtils.dprint('%s: Loaded model data\n  %s (%d keypoints)' % (self, model_filename, num_keypoints))
        except:
            IkaUtils.dprint('%s: Could not load model data. Trying to rebuild...' % self)

            calibration_image = cv2.imread('camera/ika_usbcam/Pause.png', 0)
            self.calibration_image_size = calibration_image.shape[:2]
            calibration_image_hight, calibration_image_width = \
                calibration_image.shape[ :2] 
            self.calibration_image_keypoints, self.calibration_image_descriptors = \
                self.detector.detectAndCompute( calibration_image, None)

            print(self.calibration_image_keypoints)
            print(self.calibration_image_descriptors)

            self.saveModelToFile(model_filename)
            IkaUtils.dprint('%s: Created model data')

        self.trained = True


if __name__ == "__main__":
    WarpFilterModel()
    WarpFilterModel()
    WarpFilterModel()
