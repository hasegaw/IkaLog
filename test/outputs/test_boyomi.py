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

import os
import re
import unittest

class CommentatorMock(object):
    def read(self, message):
        self.last_message = message


class TestCSVPlugin(unittest.TestCase):

    def test_init_boyomi_client(self):
        from ikalog.outputs.boyomi import BoyomiClient
        BoyomiClient()

    def test_init_boyomi_plugin(self):
        from ikalog.outputs.boyomi import BoyomiPlugin
        obj = BoyomiPlugin()
        obj._client = CommentatorMock()

        obj._do_read({ 'text': 'hello world'})
        assert obj._client.last_message == 'hello world'

    def test_boyomi_commentator(self):
        from ikalog.outputs.boyomi import BoyomiPlugin
        obj = BoyomiPlugin()
        obj._client = CommentatorMock()
        obj._client._last_mesasge = None

        obj.on_lobby_matching({})
        assert obj._client.last_message is not None


if __name__ == '__main__':
    unittest.main()
