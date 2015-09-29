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

from ikalog.utils import *

class offset:
    offset = (0, 0)

    def offsetImage(self, img):
        if (self.offset[0] == 0 and self.offset[1] == 0):
            return None

        ox = self.offset[0]
        oy = self.offset[1]

        sx1 = max(-ox, 0)
        sy1 = max(-oy, 0)

        dx1 = max(ox, 0)
        dy1 = max(oy, 0)

        w = min(self.out_width - dx1, self.out_width - sx1)
        h = min(self.out_height - dy1, self.out_height - sy1)

        new_frame = np.zeros((out_height, out_width, 3), np.uint8)
        new_frame[dy1:dy1 + h, dx1:dx1 + w] = frame[sy1:sy1 + h, sx1:sx1 + w]
        return new_frame

    def __init__(self, debug=False):
        pass
