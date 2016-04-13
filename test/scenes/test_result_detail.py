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

import sys
import json
import argparse
import pprint
import cv2

from test.scenes.scene_test import SceneTestCase
from ikalog.scenes.result_detail import ResultDetail
from ikalog.utils import IkaUtils


class TestResultDetail(SceneTestCase):
    scene_name = 'result_detail'


    def _load_scene_class(self):
        from ikalog.scenes.result_detail import ResultDetail
        return ResultDetail(None)

    def _test_scene(self, filename, params):
        obj = self._load_scene_class()
        context = self._create_context()
        context['engine']['frame'] = self._load_screenshot(filename)

        matched = obj.match(context)
        assert matched
        analyzed = obj.analyze(context)
        assert analyzed
        assert context['game']['won'] == params['won']

        return True

    def test_scoreboard_ja_nawabari_won(self):
        self._test_scene(
            'scoreboard_ja_nawabari_won.png',
            {
                'won': True,
            }
        )

    def test_scoreboard_ja_nawabari_lost(self):
        self._test_scene(
            'scoreboard_ja_nawabari_lost.png',
            {
                'won': False,
            }
        )
