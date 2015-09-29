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
import sys

import cv2

from ikalog.utils import *


class GameFinish(object):

    last_matched = False

    def match(self, context):
        frame = context['engine']['frame']

        matched = self.mask_finish.match(frame)
        ret = matched and (not self.last_matched)
        self.last_matched = matched

        return ret

    def __init__(self, debug=False):
        self.mask_finish = IkaMatcher(
            0, 0, 1280, 720,
            img_file='masks/ui_finish.png',
            threshold=0.95,
            orig_threshold=0.001,
            false_positive_method=IkaMatcher.FP_BACK_IS_BLACK,
            pre_threshold_value=16,
            label='Finish',
            debug=debug,
        )

if __name__ == "__main__":
    target = cv2.imread(sys.argv[1])
    obj = GameFinish(debug=True)

    context = {
        'engine': {'frame': target},
        'game': {},
    }

    matched = obj.match(context)
    print("matched %s" % (matched))

    cv2.waitKey()
