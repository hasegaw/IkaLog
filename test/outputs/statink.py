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

#  stat.ink プラグインが持っている日本語->ID変換が正しいことを確認する
#  ユニットテスト
#  (将来的には IkaLog 内も stat.ink 互換 ID でもつようにする)

import unittest
from ikalog import constants


class TestStatInk(unittest.TestCase):

    def _load_StatInk(self):
        from ikalog.outputs.statink import StatInk
        return StatInk('not_valid_key')

    def test_statink_stage_name(self):
        # IkaLog 文字列セットと stat.ink プラグイン内の文字列の
        # 整合性テスト
        statink = self._load_StatInk()

        for stage_key in list(constants.stages.keys()):
            stage_ja = constants.stages[stage_key]['ja']
            context = {'game': {'map': {'name': stage_ja}, }, }
            assert stage_key == statink.encode_stage_name(context)

    def test_statink_rule_name(self):
        # IkaLog 文字列セットと stat.ink プラグイン内の文字列の
        # 整合性テスト
        statink = self._load_StatInk()

        for rule_key in list(constants.rules.keys()):
            rule_ja = constants.rules[rule_key]['ja']
            context = {'game': {'rule': {'name': rule_ja}, }, }
            assert rule_key == statink.encode_rule_name(context)

    def test_statink_weapon_name(self):
        # IkaLog 文字列セットと stat.ink プラグイン内の文字列の
        # 整合性テスト
        statink = self._load_StatInk()

        for weapon_key in list(constants.weapons.keys()):
            weapon_ja = constants.weapons[weapon_key]['ja']
            assert weapon_key == statink.encode_weapon_name(weapon_ja)

    def test_statink_weapon_name2(self):
        # 画像認識された時に得られる文字列を stat.ink キーに正しく変換
        # できるかテスト
        statink = self._load_StatInk()

        from ikalog.utils import IkaGlyphRecoginizer
        weapons = IkaGlyphRecoginizer()
        weapons.load_model_from_file('data/weapons.knn.data')

        for weapon_ja in weapons.weapon_names:
            assert statink.encode_weapon_name(weapon_ja)
