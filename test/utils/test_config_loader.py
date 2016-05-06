#!/usr/bin/env python3
# -*- coding: utf-8 -*-
#
#  IkaLog
#  ======
#  Copyright (C) 2016 Takeshi HASEGAWA
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

#  Unit test for ikautils.
#  Usage:
#    python ./test_ikautils.py
#  or
#    py.test ./test_ikautils.py

import unittest
import os.path
import sys

# Append the Ikalog root dir to sys.path to import IkaUtils.
sys.path.append(os.path.join(os.path.dirname(__file__), '..', '..'))
from ikalog.utils import config_loader

class TestConfigLoader(unittest.TestCase):
    def test__replace_vars(self):
        vars = {'__INPUT_FILE__': '/tmp/video.mp4'}
        args = {'bool': True,
                'num': 123,
                'str': 'Hello',
                'file.txt': '__INPUT_FILE__.txt',
                'message': 'This is __INPUT_FILE__.',
                }
        replaced = config_loader._replace_vars(args, vars)
        self.assertTrue(replaced.get('bool'))
        self.assertEqual(123, replaced.get('num'))
        self.assertEqual('Hello', replaced.get('str'))
        self.assertEqual('/tmp/video.mp4.txt', replaced.get('file.txt'))
        self.assertEqual('This is /tmp/video.mp4.', replaced.get('message'))

if __name__ == '__main__':
    unittest.main()
