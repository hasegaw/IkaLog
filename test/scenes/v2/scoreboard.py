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

import cv2


class TestResultDetail(unittest.TestCase):
    def _get_class(self):
        from ikalog.scenes.v2.result.scoreboard.scoreboard import V2ResultScoreboard
        return V2ResultScoreboard

    def test_scoreborad_init(self):
        obj = self._get_class()(None)

    def test_scoreboard(self):
        obj = self._get_class()(None)
        a = cv2.imread('/Users/hasegaw/Dropbox/project_IkaLog/v2/raw_images/ja/result_socreboard.png')
        context = {'engine': {'frame': a}}
        r = obj.match1(context)
        assert r
