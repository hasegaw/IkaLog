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

import wx
import cv2

from ikalog.utils import *

_ = Localization.gettext_translation('IkaUI', fallback=True).gettext

class ResultsGUI(object):
    def __init__(self, ikalog_gui):
        self.ikalog_gui = ikalog_gui
        self.frame = None
        self.result_image = None
        self.size = (640, 360)
        self._init_frame()

    def _init_frame(self):
        if self.frame:
            return

        self.frame = wx.Frame(
            self.ikalog_gui.frame, wx.ID_ANY, _("Last Result"), size=self.size)
        self.draw_image()

    def show(self):
        if not self.frame:
            self._init_frame()
        self.frame.Show()
        self.frame.Raise()

    def draw_image(self):
        if not self.result_image or not self.frame:
            return
        wx.StaticBitmap(self.frame, wx.ID_ANY, self.result_image,
                        (0, 0), self.size)

    def on_game_individual_result(self, context):
        # FIXME
        return

        cv_frame = cv2.resize(context['engine']['frame'], self.size)
        img_frame_rgb = cv2.cvtColor(cv_frame, cv2.COLOR_BGR2RGB)
        height, width = img_frame_rgb.shape[0:2]

        self.result_image = wx.BitmapFromBuffer(width, height, img_frame_rgb)
        self.draw_image()
