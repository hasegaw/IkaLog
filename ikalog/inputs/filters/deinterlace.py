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

class deinterlace(ikalog.inputs.filters.filter.filter):

    def pre_execute(self, frame):
        return True

    def execute(self, img):
        if not (self.enabled):
            return img

        for y in range(img.shape[0])[1::2]:
            img[y, :] = img[y - 1, :]

        return img

    def reset(self):
        pass

    def __init__(self, parent, debug=False):
        super().__init__(parent, debug=debug)
