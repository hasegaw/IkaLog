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

import time

import cv2


class PreviewDetected(object):

    def on_frame_read(self, context):
        self.rects = [ ]

    def on_mark_rect_in_preview(self, context, rect=None):
        if rect is not None:
            self.rects.append(rect)

    def on_draw_preview(self, context):
        if not ('preview' in context['engine']):
            return


        for rect in self.rects:
            cv2.rectangle(
                context['engine']['preview'],
                rect[0], rect[1],
                color=(255, 255, 255),
                thickness=4
            )

    ##
    # Constructor
    # @param self         The Object Pointer.
    #
    def __init__(self, wait_ms=1, size=(1280, 720)):
        self.rects = []
