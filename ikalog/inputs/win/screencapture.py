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
import ctypes
import time
import threading

import cv2
import numpy as np

from ikalog.utils import *
from ikalog.inputs import VideoInput
from ikalog.inputs.filters import WarpFilter, WarpCalibrationNotFound, WarpCalibrationUnacceptableSize

_ = Localization.gettext_translation('screencapture', fallback=True).gettext


class ScreenCapture(VideoInput):

    cap_optimal_input_resolution = False

    # FIXME: Filter classes refer these variables.
    out_width = 1280
    out_height = 720

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
                _('Due to the input resultion (%d x %d) some recognition may fail unexpectedly.') % (
                    w, h),
                _('IkaLog expects 1280 x 720, or 1920 x 1080 as input resolution.'),
            ])
            IkaUtils.dprint(msg)
        else:
            return False

        self.last_capture_geom = (h, w)
        return True

    def reset(self):
        self._warp_filter = WarpFilter(self)
        self._calibration_requested = False
        super(ScreenCapture, self).reset()

    def auto_calibrate(self, img):
        try:
            r = self._warp_filter.calibrateWarp(
                img,
                validation_func=self.on_validate_warp
            )

        except WarpCalibrationUnacceptableSize as e:
            (w, h) = e.shape
            msg = '\n'.join([
                _('Current image size (%d x %d) cannot be accepted.') % (w, h),
                _('IkaLog expects 1280 x 720, or 1920 x 1080 as input resolution.'),
                _('Calibration Failed!'),
            ])
            IkaUtils.dprint(msg)
            return False

        except WarpCalibrationNotFound:
            msg = '\n'.join([
                _('Could not find any WiiU image from the desktop.'),
                _('IkaLog expects 1280 x 720, or 1920 x 1080 as input resolution.'),
                _('Calibration Failed!'),
            ])
            IkaUtils.dprint(msg)
            return False

        if not r:
            msg = '\n'.join([
                _('No description provided. (could be a bug)'),
                _('Calibration Failed!'),
            ])
            return False
            IkaUtils.dprint(msg)

        self._warp_filter.enable()
        IkaUtils.dprint(_('Calibration succeeded!'))
        return True

    def capture_screen(self):
        from PIL import ImageGrab

        try:
            img = ImageGrab.grab(None)
        except TypeError:
            # なぜ発生することがあるのか、よくわからない
            IkaUtils.dprint('%s: Failed to grab desktop image' % self)
            return None

        return cv2.cvtColor(np.asarray(img), cv2.COLOR_RGB2BGR)

    def _read_frame_func(self):
        img = self.capture_screen()

        if self._calibration_requested:
            self._calibration_requested = False
            self.auto_calibrate(img)

        img = self._warp_filter.execute(img)

        return img

    def on_key_press(self, context, key):
        if (key == ord('c') or key == ord('C')):
            # 次回キャリブレーションを行う
            self._calibration_requested = True

    def _is_active_func(self):
        return True

    def _initialize_driver_func(self):
        pass

    def _cleanup_driver_func(self):
        pass

    def _select_device_by_index_func(self, source):
        IkaUtils.dprint(
            '%s: Does not support _select_device_by_index_func()' % self)

    def _select_device_by_name_func(self, source):
        IkaUtils.dprint(
            '%s: Does not support _select_device_by_name_func()' % self)

if __name__ == "__main__":
    obj = ScreenCapture()

    k = 0
    while k != 27:
        frame = obj.read_frame()
        if frame is not None:
            cv2.imshow(obj.__class__.__name__, frame)
        k = cv2.waitKey(1)
        obj.on_key_press(None, k)
