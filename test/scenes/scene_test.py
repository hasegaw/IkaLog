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

import unittest
import os
import cv2

class SceneTestCase(unittest.TestCase):

    @classmethod
    def _load_screenshot(cls, filename, scene = None):
        if scene is None:
            scene = cls.scene_name

        assert scene is not None

        filepath = os.path.join('test_data', 'screenshots',
            scene, filename)
        img = cv2.imread(filepath)
        assert img is not None, 'Failed to read screenshot %s' % filepath
        return img

