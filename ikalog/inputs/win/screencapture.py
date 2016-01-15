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

import gettext
import os
import sys
import time

import cv2
import numpy as np

from ikalog.inputs.filters import WarpFilter
from ikalog.utils import IkaUtils, Localization

_ = Localization.gettext_translation('screencapture', fallback=True).gettext

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

    # on_valide_warp
    # Handler being called by warp calibration process.
    # Caller passes the four edge points in raw image to crop game screen.
    #
    # Return True to approve the points. Calibration process can be canceled
    # by passing False.
    #
    # @param self The object pointer.
    # @param points Points. [ left_top, right_top, right_bottom, left_bottom ]
    # @return Approve (True) or delcline (False).
    def on_validate_warp(self, points):
        w = int(points[1][0] - points[0][0])
        h = int(points[2][1] - points[1][1])
        print('on_validate_warp: ', w, h)

        acceptable_geoms = [[720, 1280], [1080, 1920]]

        acceptable = False
        exact = False
        for geom in acceptable_geoms:
            if (geom[0] - 3 < h) and (h < geom[0] + 3):
                if (geom[1] - 3 < w) and (w < geom[1] + 3):
                    acceptable = True

            if geom[0] == h and geom[1] == w:
                exact = True

        if exact:
            pass

        elif acceptable:
            msg = '\n'.join([
                _('Calibration succeeded!'),
                _('Due to the input resultion (%d x %d) some recognition may fail unexpectedly.') % (w, h),
                _('IkaLog expects 1280 x 720, or 1920 x 1080 as input resolution.'),
            ])
            try:
                r = wx.MessageDialog(None, msg, _('Warning'),
                                     wx.OK | wx.ICON_ERROR).ShowModal()
            except:
                IkaUtils.dprint(msg)
        else:
            return False

        self.last_capture_geom = (h, w)
        return True

    def auto_calibrate(self, img):
        r = self._warp_filter.calibrateWarp(
            img,
            validation_func=self.on_validate_warp
        )
        if r:
            self._warp_filter.enable()
            IkaUtils.dprint(_('Calibration succeeded!'))
            return True
        else:
            msg = '\n'.join([
                _('Calibration failed! Cannot detect WiiU display.'),
                _('IkaLog expects 1280 x 720, or 1920 x 1080 as input resolution.'),
            ])
            try:
                r = wx.MessageDialog(None, msg, _('Warning'),
                                     wx.OK | wx.ICON_ERROR).ShowModal()
            except:
                IkaUtils.dprint(msg)
            return False

    def read_raw(self):
        from PIL import ImageGrab

        try:
            img = ImageGrab.grab(None)
        except TypeError:
            # なぜ発生することがあるのか、よくわからない
            IkaUtils.dprint('%s: Failed to grab desktop image' % self)
            return None

        img = np.asarray(img)
        return img

    def read(self):
        img = self.read_raw()

        if img is None:
            return None, None

        if self._calibration_requested:
            self._calibration_requested = False
            img_bgr = cv2.cvtColor(img, cv2.COLOR_RGB2BGR)
            self.auto_calibrate(img_bgr)

        img = self._warp_filter.execute(img)

        img = cv2.resize(img, (self._out_width, self._out_height))

        img = cv2.cvtColor(img, cv2.COLOR_RGB2BGR)
        t = self._time() - self._launch
        return (img, t)

    def on_key_press(self, context, key):
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

    def reset(self):
        self._warp_filter = WarpFilter(self)

    def __init__(self, bbox=None):
        '''
        bbox -- bbox Crop bounding box as (x, y, w, h)
        '''
        self._check_import()
        self.last_input_geom = None

        self._launch = self._time()

        self._warp_filter = WarpFilter(self)
        self._calibration_requested = False
        if bbox is not None:
            self._warp_filter.set_bbox(
                bbox[0], bbox[1], bbox[2], bbox[3],
            )
            self._warp_filter.enable()

        IkaUtils.dprint('%s: initalizing screen capture' % (self))

if __name__ == "__main__":
    obj = ScreenCapture()

    k = 0
    while k != 27:
        frame, t = obj.read()
        cv2.imshow(obj.__class__.__name__, frame)
        print(t)
        k = cv2.waitKey(1)
        obj.on_key_press(None, k)
