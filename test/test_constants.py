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

#  Unit test for constants, and IDs.

import urllib3
import unittest
import json


class TestConstants(unittest.TestCase):

    def _load_constants_module(self):
        from ikalog import constants
        return constants

    def _fetch_statink_v1_weapons(self):
        url = 'https://stat.ink/api/v1/weapon'
        pool = urllib3.PoolManager()

        req = pool.urlopen('GET', url)
        self._statink_v1_weapons = json.loads(req.data.decode('utf-8'))

    def _get_statink_v1_weapons(self):
        if not hasattr(self, '_statink_v1_weapons'):
            self._fetch_statink_v1_weapons()

        return self._statink_v1_weapons

    def _fetch_statink_v1_stages(self):
        url = 'https://stat.ink/api/v1/map'
        pool = urllib3.PoolManager()

        req = pool.urlopen('GET', url)
        self._statink_v1_stages = json.loads(req.data.decode('utf-8'))

    def _get_statink_v1_stages(self):
        if not hasattr(self, '_statink_v1_stages'):
            self._fetch_statink_v1_stages()

        return self._statink_v1_stages

    def _fetch_statink_v1_rules(self):
        url = 'https://stat.ink/api/v1/rule'
        pool = urllib3.PoolManager()

        req = pool.urlopen('GET', url)
        self._statink_v1_rules = json.loads(req.data.decode('utf-8'))

    def _get_statink_v1_rules(self):
        if not hasattr(self, '_statink_v1_rules'):
            self._fetch_statink_v1_rules()

        return self._statink_v1_rules

    def _get_statink_v1_gears(self, gear_type):
        return self._fetch_statink_v1_gears(gear_type)

    def _fetch_statink_v1_gears(self, gear_type):
        assert gear_type in ['headgear', 'clothing', 'shoes']
        url = 'https://stat.ink/api/v1/gear?type=%s' % gear_type
        pool = urllib3.PoolManager()

        req = pool.urlopen('GET', url)
        return json.loads(req.data.decode('utf-8'))

    #
    # Test Cases
    #

    def test_statink_weapons_lookup_by_statink_key(self):
        statink_weapons = self._get_statink_v1_weapons()
        weapons = self._load_constants_module().weapons
        upcoming_weapons = self._load_constants_module().upcoming_weapons

        error_list = []
        for statink_weapon in statink_weapons:
            statink_key = statink_weapon['key']

            found = (statink_key in weapons)
            if not found:
                if not (statink_key in upcoming_weapons):
                    error_list.append(
                        'IkaLog does not have key %s' % statink_key)

        assert len(error_list) == 0, '\n'.join(error_list)

    def test_statink_weapons_lookup_by_ikalog_key(self):
        statink_weapons = self._get_statink_v1_weapons()
        weapons = self._load_constants_module().weapons

        error_list = []
        for ikalog_key in weapons.keys():
            found = False
            for statink_weapon in statink_weapons:
                found = found or (statink_weapon['key'] == ikalog_key)
            if not found:
                error_list.append('stat.ink does not have key %s' % ikalog_key)

        assert len(error_list) == 0, '\n'.join(error_list)

    def _test_statink_gears_lookup(self, gear_type, d):
        statink_gears = self._get_statink_v1_gears(gear_type)
        statink_keys = list(map(lambda g: g['key'], statink_gears))
        ikalog_keys = list(d.keys())

        assert len(statink_keys) > 1
        assert len(ikalog_keys) > 1

        all_keys = []
        all_keys.extend(statink_keys)
        all_keys.extend(ikalog_keys)

        error_list = []
        for key in all_keys:
            if (key in statink_keys) and (key in ikalog_keys):
                continue

            if not (key in statink_keys):
                error_list.append('stat.ink doesn''t have key %s' % key)

            if not (key in ikalog_keys):
                error_list.append('IkaLog doesn''t have key %s' % key)

        if len(error_list) > 0:
            print(error_list)
            raise Exception()

    def test_statink_gears_lookup(self):
        from ikalog import constants
        self._test_statink_gears_lookup('headgear', constants.gear_headgear)
        self._test_statink_gears_lookup('clothing', constants.gear_clothing)
        self._test_statink_gears_lookup('shoes', constants.gear_shoes)

    def _test_classifier_gears_lookup(self, classifier, d):
        constant_keys = list(d.keys())
        classifier_keys = list(classifier.icon_names)
        all_keys = []
        all_keys.extend(constant_keys)
        all_keys.extend(classifier_keys)

        error_list = []
        for key in all_keys:
            if (key in classifier_keys) and (key in constant_keys):
                continue

            if not (key in classifier_keys):
                error_list.append('the classifier doesn''t have key %s' % key)

            if not (key in constant_keys):
                error_list.append('IkaLog doesn''t have key %s' % key)

        if len(error_list) > 0:
            print(error_list)
            raise Exception()

    def test_classifier_gears_lookup(self):
        from ikalog.utils.icon_recoginizer import GearRecoginizer
        from ikalog import constants

        headgear_classifier = GearRecoginizer('data/gears_head.knn.data')
        headgear_classifier.load_model_from_file()
        headgear_classifier.knn_train()

        clothing_classifier = GearRecoginizer('data/gears_clothing.knn.data')
        clothing_classifier.load_model_from_file()
        clothing_classifier.knn_train()

        shoes_classifier = GearRecoginizer('data/gears_shoes.knn.data')
        shoes_classifier.load_model_from_file()
        shoes_classifier.knn_train()

        self._test_classifier_gears_lookup(
            headgear_classifier, constants.gear_headgear)

    def test_death_reason_lookup_by_weapon_key(self):
        from ikalog.utils.character_recoginizer.deadly_weapon import DeadlyWeaponRecoginizer
        deadly_weapons = DeadlyWeaponRecoginizer()

        weapons = self._load_constants_module().weapons

        death_reasons = list(weapons.keys())
        death_reasons.extend(self._load_constants_module().deadly_sub_weapons)
        death_reasons.extend(
            self._load_constants_module().deadly_special_weapons)
        death_reasons.extend(
            ['hoko_shot', 'hoko_barrier', 'hoko_inksplode', 'propeller'])

        error_list = []
        # 順方向
        for death_reason in death_reasons:
            try:
                deadly_weapons.name2id_table.index(death_reason)
            except ValueError:
                error_list.append(
                    'deadly_weapons does not have key: %s' % death_reason)

        # 逆方向
        for death_reason in deadly_weapons.name2id_table:
            try:
                death_reasons.index(death_reason)
            except ValueError:
                error_list.append(
                    'deadly_weapons has a weird key: %s' % death_reason)

        print("\n".join(error_list))
        assert len(error_list) == 0

    def test_stages(self):
        statink_stages = self._get_statink_v1_stages()
        stages = self._load_constants_module().stages
        assert len(statink_stages) == len(list(stages.keys()))

        error_list = []
        for statink_stage in statink_stages:
            stage_key = statink_stage['key']
            if not (stage_key in stages):
                error_list.append('stages does not have a key: %s' % stage_key)

        print("\n".join(error_list))
        assert len(error_list) == 0

    def test_rules(self):
        statink_rules = self._get_statink_v1_rules()
        rules = self._load_constants_module().rules
        assert len(statink_rules) == len(list(rules.keys()))

        error_list = []
        for statink_rule in statink_rules:
            rule_key = statink_rule['key']
            if not (rule_key in rules):
                error_list.append('rules does not have a key: %s' % rule_key)

        print("\n".join(error_list))
        assert len(error_list) == 0

# データ形式
# [{'key': '52gal',
# 'name': {'en_US': '.52 Gal', 'ja_JP': '.52ガロン'},
# 'special': {'key': 'megaphone',
# 'name': {'en_US': 'Killer Wail', 'ja_JP': 'メガホンレーザー'}},
# 'sub': {'key': 'splashshield',
# 'name': {'en_US': 'Splash Wall', 'ja_JP': 'スプラッシュシールド'}},
# 'type': {'key': 'shooter', 'name': {'en_US': 'Shooters', 'ja_JP': 'シューター'}}},
