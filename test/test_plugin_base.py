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

from ikalog.plugin import IkaLogPlugin
import unittest


class MockPlugin(IkaLogPlugin):

    def on_set_configuration(self, config):
        self.config = config

    def on_validate_configuration(self, config):
        assert 'hoge' in config
        return True


class TestPluginBase(unittest.TestCase):

    def test_plugin_mock(self):
        obj = MockPlugin()
        assert obj.get_configuration().__class__.__name__ == 'dict'

        try:
            obj.set_configuration({'hello': 'world'})
            raise Exception('Should not reach here')
        except AssertionError:
            pass

        obj.set_configuration({'hello': 'world', 'hoge': 'fuga'})

if __name__ == '__main__':
    unittest.main()
