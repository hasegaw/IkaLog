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
from ikalog.utils import IkaUtils

class IkaMatcherMock(object):
    def __init__(self, id):
        self.id_ = id

class TestIkaUtils(unittest.TestCase):

    #
    # Test Cases
    #
    def test_extend_languages(self):
        # Default languages
        self.assertIsNotNone(IkaUtils.extend_languages(None))

        # The specified language(s) should be in the beginning.
        # 'en' and 'ja' as fallback languages should also exist.
        languages = IkaUtils.extend_languages('??')
        self.assertEqual('??', languages[0])
        self.assertTrue('en' in languages)
        self.assertTrue('ja' in languages)

        # Input can be a list.
        languages = IkaUtils.extend_languages(['ja', 'fr'])
        self.assertEqual('ja', languages[0])
        self.assertEqual('fr', languages[1])
        self.assertTrue('en' in languages)
        self.assertTrue('ja' in languages)


    def test_map2text(self):
        map_mock = IkaMatcherMock('kinmedai')

        # English
        self.assertEqual('Museum d\'Alfonsino',
                         IkaUtils.map2text(map_mock, languages='en'))

        # Japanese
        self.assertEqual('キンメダイ美術館',
                         IkaUtils.map2text(map_mock, languages='ja'))

        # Fallback to English
        self.assertEqual('Museum d\'Alfonsino',
                         IkaUtils.map2text(map_mock, languages='??'))

        # Multiple languages
        self.assertEqual('キンメダイ美術館',
                         IkaUtils.map2text(map_mock, languages=['ja', 'en']))

        # Unkonwn
        unknown_map_mock = IkaMatcherMock('unknown')
        self.assertEqual('?', IkaUtils.map2text(unknown_map_mock))
        self.assertEqual('<:=',
                         IkaUtils.map2text(unknown_map_mock, unknown='<:='))


    def test_rule2text(self):
        rule_mock = IkaMatcherMock('area')

        # English
        self.assertEqual('Splat Zones',
                         IkaUtils.rule2text(rule_mock, languages='en'))

        # Japanese
        self.assertEqual('ガチエリア',
                         IkaUtils.rule2text(rule_mock, languages='ja'))

        # Fallback to English
        self.assertEqual('Splat Zones',
                         IkaUtils.rule2text(rule_mock, languages='??'))

        # Multiple languages
        self.assertEqual('ガチエリア',
                         IkaUtils.rule2text(rule_mock, languages=['ja', 'en']))

        # Unkonwn
        unknown_rule_mock = IkaMatcherMock('unknown')
        self.assertEqual('?', IkaUtils.rule2text(unknown_rule_mock))
        self.assertEqual('<:=',
                         IkaUtils.rule2text(unknown_rule_mock, unknown='<:='))


    def test_gear_ability2text(self):
        gear_mock = IkaMatcherMock('ninja_squid')

        # English
        self.assertEqual('Ninja Squid',
                         IkaUtils.gear_ability2text(gear_mock, languages='en'))

        # Japanese
        self.assertEqual('イカニンジャ',
                         IkaUtils.gear_ability2text(gear_mock, languages='ja'))

        # Fallback to English
        self.assertEqual('Ninja Squid',
                         IkaUtils.gear_ability2text(gear_mock, languages='??'))

        # Multiple languages
        self.assertEqual('イカニンジャ',
                         IkaUtils.gear_ability2text(gear_mock,
                                                    languages=['ja', 'en']))

        # Unkonwn
        unknown_gear_mock = IkaMatcherMock('unknown')
        self.assertEqual('?', IkaUtils.gear_ability2text(unknown_gear_mock))
        self.assertEqual('<:=',
                         IkaUtils.gear_ability2text(unknown_gear_mock,
                                                    unknown='<:='))


if __name__ == '__main__':
    unittest.main()
