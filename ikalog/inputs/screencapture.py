#!/usr/bin/env python3
# -*- coding: utf-8 -*-
#
#  IkaLog
#  ======
#  Copyright (C) 2015 ExceptionError
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

import os
import sys
import time

import cv2
import numpy as np

from ikalog.inputs.filters import WarpFilter
from ikalog.utils import IkaUtils


class ScreenCapture(object):
    ''' ScreenCapture input plugin
    This plugin depends on python-pillow ( https://pillow.readthedocs.org/ ).
    This plugin now supports only IkaLog.py.
    You can use this plugin if you modify IkaConfig.py
    ```
from ikalog.inputs.screencapture import ScreenCapture

class IkaConfig:
    def config(self):
        source = ScreenCapture()
    ```
    '''
    from_file = False

    _out_width = 1280
    _out_height = 720

    # FIXME: Filter classes refer these variables.
    out_width = 1280
    out_height = 720

    _launch = 0

    def auto_calibrate(self, img):
        self._offset_filter.calibrateWarp(img)
        self._offset_filter.enable()

    def read(self):
        from PIL import ImageGrab

        img = ImageGrab.grab(None)
        img = np.asarray(img)

        if self._calibration_requested:
            self._calibration_requested = False
            img_bgr = cv2.cvtColor(img, cv2.COLOR_RGB2BGR)
            self.auto_calibrate(img_bgr)

        img = self._offset_filter.execute(img)

        img = cv2.cvtColor(img, cv2.COLOR_RGB2BGR)
        t = self._time() - self._launch
        return (img, t)

    def onKeyPress(self, context, key):
        if (key == ord('c') or key == ord('C')):
            # 次回キャリブレーションを行う
            self._calibration_requested = True

    def _time(self):
        return int(time.time() * 1000)

    def _check_import(self):
        try:
            from PIL import ImageGrab
        except:
            sys.exit(
                "モジュール python-pillow がロードできませんでした。\n" +
                "インストールするには以下のコマンドを利用してください。\n" +
                "pip install Pillow"
            )

    def __init__(self, bbox=None):
        '''
        bbox -- bbox Crop bounding box as (x, y, w, h)
        '''
        self._check_import()

        self._launch = self._time()

        self._offset_filter = WarpFilter(self)
        self._calibration_requested = False
        if bbox is not None:
            self._offset_filter.set_bbox(
                bbox[0], bbox[1], bbox[2], bbox[3],
            )
            self._offset_filter.enable()

        IkaUtils.dprint('%s: initalizing screen capture' % (self))

if __name__ == "__main__":
    obj = ScreenCapture()

    k = 0
    while k != 27:
        frame, t = obj.read()
        cv2.imshow(obj.__class__.__name__, frame)
        print(t)
        k = cv2.waitKey(1)
        obj.onKeyPress(None, k)
