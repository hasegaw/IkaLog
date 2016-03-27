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

#  Unittests for commentator.py.
#  Usage:
#    python ./test_commentator.py
#  or
#    py.test ./test_commentator.py

import unittest
import os.path
import sys

# Append the Ikalog root dir to sys.path to import Commentator.
sys.path.append(os.path.join(os.path.dirname(__file__), '..', '..'))
from ikalog.outputs.commentator import Commentator

class TestIkaUtils(unittest.TestCase):
    def test__death_reason_label(self):
        # _death_reason_lable is only for Japanese at this moment.
        commentator = Commentator()
        # Custom read
        self.assertEqual('ごーにーガロン',
                         commentator._death_reason_label('52gal'))
        # Weapons
        self.assertEqual('わかばシューター',
                         commentator._death_reason_label('wakaba'))
        # Sub weapons
        self.assertEqual('チェイスボム',
                         commentator._death_reason_label('chasebomb'))
        # Special weapons
        self.assertEqual('トルネード',
                         commentator._death_reason_label('tornado'))
        # Hurtable objects
        self.assertEqual('プロペラから飛び散ったインク',
                         commentator._death_reason_label('propeller'))

        # OOB is treated in a different function.

        # Unknown
        self.assertEqual('未知の武器',
                         commentator._death_reason_label('530000gal'))

if __name__ == '__main__':
    unittest.main()
