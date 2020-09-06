#!/usr/bin/env python3
# -*- coding: utf-8 -*-
#
#  IkaLog
#  ======
#  Copyright (C) 2017 Takeshi HASEGAWA
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

from ikalog.scenes.v2.result.scoreboard.transform  import transform_scoreboard
from ikalog.scenes.v2.result.scoreboard.extract import extract_players

import cv2
import numpy as np
from ikalog.utils import image_filters




def analyze(frame):
    """
    Extract sub images from the frame
    """
    players = extract_players(frame)

    """
    TODO: Perform number and image recognition
    """


    return players


if __name__ == '__main__':
    import sys
    img = cv2.imread(sys.argv[1], 1)
    # img = cv2.imread('/Users/hasegaw/Dropbox/project_IkaLog/v2/raw_images/ja/result_socreboard.png', 1)
    print(analyze(img))
#    cv2.waitKey()
