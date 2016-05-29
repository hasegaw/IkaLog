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

    def test_game_index(self):
        engine = ikalog.engine.IkaEngine()
        engine.reset()
        context = engine.context

        self.assertEqual(0, context['game']['index'])

        context['game']['index'] = 3
        engine.reset()
        self.assertEqual(3, context['game']['index'])

        # The second sequential reset() should not increase the index.
        engine.reset()
        self.assertEqual(3, context['game']['index'])

        # After session_close, index should be incremented.
        # Note: We can change the timing of the increment from game_end to
        #       game_start later, if necessary.
        engine.session_close()
        self.assertEqual(4, context['game']['index'])

        # After session_abort also increases the index. Output plugins should
        # take care about if session_close was called before.
        engine.session_abort()
        self.assertEqual(5, context['game']['index'])

    def test_set_epoch_time(self):
        engine = ikalog.engine.IkaEngine()
        engine.reset()
        context = engine.context

        # None is the default as the current time.
        self.assertIsNone(context['engine']['epoch_time'])

        IKA_EPOCH = time.mktime(time.strptime('20150528_123456',
                                              '%Y%m%d_%H%M%S'))
        engine.set_epoch_time('20150528_123456')
        self.assertEqual(IKA_EPOCH, context['engine']['epoch_time'])

        # '' or None does not change the current value.
        engine.set_epoch_time('')
        self.assertEqual(IKA_EPOCH, context['engine']['epoch_time'])
        engine.set_epoch_time(None)
        self.assertEqual(IKA_EPOCH, context['engine']['epoch_time'])

        # None is the default as the current time.
        engine.set_epoch_time('now')
        self.assertIsNone(context['engine']['epoch_time'])

if __name__ == '__main__':
    unittest.main()
