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

import ikalog.inputs.filters.filter
from ikalog.utils import *

class white_balance(ikalog.inputs.filters.filter.filter):

    def getColorBalance(self, img):
        r = (1052, 41, 70, 41)
        white = img[r[1]:r[1] + r[3], r[0]: r[0] + r[2], :]

        avg_b = np.average(white[:, :, 0]) * 1.0
        avg_g = np.average(white[:, :, 1]) * 1.0
        avg_r = np.average(white[:, :, 2]) * 1.0

        avg = np.average(white)

        coff_b = (avg / avg_b)
        coff_g = (avg / avg_g)
        coff_r = (avg / avg_r)

        return avg, (avg_b, avg_g, avg_r), (coff_b, coff_g, coff_r)

    def pre_execute(self, img):
        return (self.coffs is not None)

    def execute(self, img):
        if not (self.pre_execute(img)):
            return img
        return self.filterImage(img)
            
    def filterImage(self, img, coffs = None):
        if coffs is None:
            coffs = self.coffs

        if coffs is None:
            return img

        img_work = np.array(img, np.float32)

        for n in range(len(coffs)):
            img_work[:, :, n] = img_work[:, :, n] * coffs[n]
            img_work[img_work > 255] = 255

        return np.array(img_work, np.uint8)

    def calibrateColor(self, capture_image):
        img_720p = cv2.resize(capture_image, (1280, 720))
        avg, avgs, coffs = self.getColorBalance(img_720p)
        print('source avg', avg, avgs)
        print('source coff', coffs)

        # HDMI input sample (reference image)
        #img_hdmi = cv2.imread('camera/color_balance/pause_hdmi.bmp')
        #img_hdmi_720p = cv2.resize(img_hdmi, (1280, 720))
        #avg_hdmi, avgs_hdmi, coffs_hdmi = self.getColorBalance(img_hdmi_720p)
        #
        #print('HDMI   avg', avg_hdmi, avgs_hdmi)
        #print('HDMI   coff', coffs_hdmi)
        avg_hdmi = 233.203252033

        # gain
        coffs_with_gain = (
            coffs[0] * avg_hdmi / avg,
            coffs[1] * avg_hdmi / avg,
            coffs[2] * avg_hdmi / avg,
        )

        img_out = self.filterImage(img_720p, coffs_with_gain)
        avg_out, avgs_out, coffs_out = self.getColorBalance(img_out)

        print('output avg', avg_out)

        self.coffs = coffs_with_gain

    def reset(self):
        self.coffs = None

    def __init__(self, parent, debug=False):
        super().__init__(parent, debug=debug)
        
        self.img_hdmi = cv2.imread('camera/color_balance/pause_hdmi.bmp')
