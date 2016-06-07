#!/usr/bin/env python3
# -*- coding: utf-8 -*-
#
#  IkaLog
#  ======
#  Copyright (C) 2016 Takeshi HASEGAWA
#  Copyright (C) 2016 Hiroyuki KOMATSU
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

#  Unit test for engine.
#  Usage:
#    python ./test_engine.py
#  or
#    py.test ./test_engine.py

import unittest
import os.path
import sys
import time

# Append the Ikalog root dir to sys.path to import IkaUtils.
sys.path.append(os.path.join(os.path.dirname(__file__), '..'))
import ikalog.engine
from ikalog.utils import *

class TestEngine(unittest.TestCase):
    def test_reset(self):
        engine = ikalog.engine.IkaEngine()
        engine.reset()
        context = engine.context
        self.assertTrue('game' in context)
        self.assertIsNone(context['game']['map'])
        self.assertIsNone(context['game']['rule'])
        self.assertIsNone(context['game']['start_time'])
        self.assertIsNone(context['game']['end_time'])

    def test_copy_context(self):
        engine = ikalog.engine.IkaEngine()
        engine.reset()
        context = IkaUtils.copy_context(engine.context)
        self.assertEqual(context['game']['kills'],
                         engine.context['game']['kills'])
        context['game']['kills'] = 99
        self.assertNotEqual(context['game']['kills'],
                            engine.context['game']['kills'])


if __name__ == '__main__':
    unittest.main()
