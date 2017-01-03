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

from ikalog.outputs.screenshot import *
import unittest


class TestScreenshotPlugin(unittest.TestCase):
    def test_plugin(self):
        obj = ScreenshotPlugin()
        assert obj.get_configuration()['enabled'] == False

        obj.set_configuration({'dest_dir': 'screenshots', 'enabled': True})
        assert obj.get_configuration()['enabled'] == True

        try:
            obj.set_configuration({'dest_dir': 'nonexistest_dir', 'enabled': True})
            raise Exception('Should not reach here')
        except AssertionError:
            pass


if __name__ == '__main__':
    unittest.main()
