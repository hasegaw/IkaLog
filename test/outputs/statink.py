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
from ikalog import constants


class TestStatInk(unittest.TestCase):

    def _load_StatInk(self):
        from ikalog.outputs.statink import StatInk
        return StatInk('not_valid_key')

    def test_composite(self):
        statink = self._load_StatInk()

        context = {
            'game': {
                'map': None,
                'rule': None,
                'is_fes': False,
                'won': True,
                'players': [
                    {'me': True, },
                ],
                'death_reasons': {},
            },
            'lobby': {},
            'scenes': {},
        }

        payload = statink.composite_payload(context)

        # map

        assert not 'map' in payload

        # FIXME: 現状の実装だと単体テストができない

        # context['game']['map'] = {'name': 'ホッケふ頭'}
        # payload = statink.composite_payload(context)
        # assert payload['map'] == 'hokke'

        # rule

        assert not 'rule' in payload

        context['game']['rule'] = {'name': 'ナワバリバトル'}
        payload = statink.composite_payload(context)
        assert payload['rule'] == 'nawabari'

        # local inkling's stats
        context['game']['players'] = [{
            'me': True,
            'kills': 1,
            'deaths': 2,
            'rank': 3,
            'score': 4,
            'udemae_pre': 'a',
        }, ]
        payload = statink.composite_payload(context)
        assert payload['kill'] == 1
        assert payload['death'] == 2
        assert payload['level'] == 3
        assert payload['my_point'] == 4
        assert payload['rank'] == 'a'

        # death_reasons

        context['game']['death_reasons'] = {'trap': 1}
        payload = statink.composite_payload(context)
        assert payload['death_reasons']['trap'] == 1

        # ResultJudge

        assert not 'knockout' in payload

        context['game']['rule'] = {'name': 'ナワバリバトル'}
        context['game']['knockout'] = True
        payload = statink.composite_payload(context)
        # ナワバリバトルではノックアウトが発生しないので
        # ペイロードにはのってこない。
        assert not 'knockout' in payload

        # ガチヤグラなどではOK
        context['game']['rule'] = {'name': 'ガチヤグラ'}
        payload = statink.composite_payload(context)
        assert payload['knock_out'] == 'yes'

        context['game']['knockout'] = False
        payload = statink.composite_payload(context)
        assert payload['knock_out'] == 'no'

        # ResultUdemae

        context['scenes']['result_udemae'] = {}
        context['scenes']['result_udemae']['udemae_exp_pre'] = 10
        context['scenes']['result_udemae']['udemae_exp_after'] = 20
        context['scenes']['result_udemae']['udemae_str_pre'] = 'a'
        context['scenes']['result_udemae']['udemae_str_after'] = 'a+'

        payload = statink.composite_payload(context)
        assert payload['rank_exp'] == 10
        assert payload['rank_exp_after'] == 20
        # assert payload['rank'] == 10
        assert payload['rank_after'] == 'a+'

        # ResultGears

        context['scenes']['result_gears'] = {}
        context['scenes']['result_gears']['cash'] = 10
        payload = statink.composite_payload(context)

        # TODO # assert payload['cash'] == 'a+'
        assert payload['cash_after'] == 10

        # TODO: Screenshot

        # Team Colors
        context['game']['my_team_color'] = {
            'hsv': [80, 200, 250],
            'rgb': [110, 210, 151],
        }
        context['game']['counter_team_color'] = {
            'hsv': [160, 100, 150],
            'rgb': [210, 110, 251],
        }
        payload = statink.composite_payload(context)
        assert payload['my_team_color']['hue'] == 80 * 2
        assert payload['his_team_color']['hue'] == 160 * 2

        # TODO: Test RGB data
