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

import unittest

import numpy as np


def _get_StatInkCompositor():
    from ikalog.outputs.statink.compositor import StatInkCompositor
    return StatInkCompositor


class StatInkMock(object):

    def __init__(self):
        self.img_scoreboard = np.zeros((720, 1280, 3), dtype=np.uint8)
        self.img_gears = np.zeros((720, 1280, 3), dtype=np.uint8)
        self.img_judge = np.zeros((720, 1280, 3), dtype=np.uint8)
        self.config = {'anon_others': False, 'anon_all': False}


class TestStatInk(unittest.TestCase):

    def test_lobby(self):
        obj = _get_StatInkCompositor()(None)

        payload = {}

        # standard battle
        context = {'lobby': {'type': 'public'}, 'game': {'is_fes': False}}
        obj.composite_lobby(context, payload)
        assert payload['lobby'] == 'standard'

        # private battle
        context = {'lobby': {'type': 'private'}, 'game': {'is_fes': False}}
        obj.composite_lobby(context, payload)
        assert payload['lobby'] == 'private'

        # splatfest
        context = {'lobby': {'type': 'festa'}, 'game': {'is_fes': False}}
        obj.composite_lobby(context, payload)
        assert payload['lobby'] == 'fest'

        context = {'lobby': {'type': None}, 'game': {'is_fes': True}}
        obj.composite_lobby(context, payload)
        assert payload['lobby'] == 'fest'

        context = {'lobby': {'type': 'festa'}, 'game': {'is_fes': True}}
        obj.composite_lobby(context, payload)
        assert payload['lobby'] == 'fest'

        # squad battle
        context['game'] = {'is_fes': False}
        context['lobby'] = {'type': 'tag', 'team_members': 2}
        obj.composite_lobby(context, payload)
        assert payload['lobby'] == 'squad_2'

        context['game'] = {'is_fes': False}
        context['lobby'] = {'type': 'tag', 'team_members': 3}
        obj.composite_lobby(context, payload)
        assert payload['lobby'] == 'squad_3'

        context['game'] = {'is_fes': False}
        context['lobby'] = {'type': 'tag', 'team_members': 4}
        obj.composite_lobby(context, payload)
        assert payload['lobby'] == 'squad_4'

        # wrong key
        context['game'] = {'is_fes': False}
        context['lobby'] = {'type': 'tag', 'team_members': 5}
        obj.composite_lobby(context, payload)
        assert not payload.get('lobby')

        # no lobby data => no lobby info in payload
        del context['lobby']
        obj.composite_lobby(context, payload)
        assert not payload.get('lobby')

    def test_composite_stage_and_mode(self):
        obj = _get_StatInkCompositor()(None)

        payload = {}
        context = {'game': {'map': 'arowana', 'rule': 'nawabari'}}
        obj.composite_stage_and_mode(context, payload)
        assert payload['map'] == 'arowana'
        assert payload['rule'] == 'nawabari'

        payload = {}
        context = {'game': {'map': 'izakaya', 'rule': 'motsunabe'}}
        obj.composite_stage_and_mode(context, payload)
        assert not payload.get('map')
        assert not payload.get('rule')

    def test_composite_kill_death(self):
        obj = _get_StatInkCompositor()(None)

        context = {}
        payload = {}
        obj.composite_kill_death(context, payload)

        context = {'game': {'death_reasons': {'dynamo': 10, 'liter_3k': 100}}}
        obj.composite_kill_death(context, payload)
        assert payload['death_reasons']['dynamo'] == 10
        assert payload['death_reasons']['liter_3k'] == 100

        context['game']['max_kill_combo'] = 2
        context['game']['max_kill_streak'] = 5
        obj.composite_kill_death(context, payload)
        assert payload['max_kill_combo'] == 2
        assert payload['max_kill_streak'] == 5

    def test_composite_team_colors(self):
        obj = _get_StatInkCompositor()(None)

        context = {'game': {}}
        payload = {}
        context['game'] = {
            'my_team_color': {'hsv': [45, 0, 0], 'rgb': 'deadbe'},
            'counter_team_color': {'hsv': [90, 0, 0], 'rgb': 'adbeef'},
        }
        obj.composite_team_colors(context, payload)

        assert payload['my_team_color']['hue'] == 90
        assert payload['my_team_color']['rgb'] == 'deadbe'
        assert payload['his_team_color']['hue'] == 180
        assert payload['his_team_color']['rgb'] == 'adbeef'

        conetxt = {}
        payload = {}
        obj.composite_team_colors(context, payload)

    def test_composite_agent_information(self):
        obj = _get_StatInkCompositor()(None)
        payload = {}
        context = {}
        obj.composite_agent_information(context, payload)
        assert payload['agent'] == 'IkaLog'
        assert payload['agent_version']

    def test_composite_agent_variables(self):
        return True

    def test_composite_result_judge_turf(self):
        return True

    def test_composite_result_judge_ranked(self):
        return True

    def test_composite_result_scorebord(self):
        return True

    def test_composite_result_gears(self):
        return True

    def test_composite_result_udemae(self):
        obj = _get_StatInkCompositor()(None)
        payload = {'rule': 'nawabari'}

        context = {'game': {
            'result_udemae_str_pre': 's+',
            'result_udemae_str': 's',
            'result_udemae_exp_pre': 99,
            'result_udemae_exp': 70,
        }}
        obj.composite_result_udemae(context, payload)
        assert not ('rank' in payload)  # rule == nawabari

        payload = {'rule': 'yagura'}
        obj.composite_result_udemae(context, payload)
        assert payload['rank'] == 's+'
        assert payload['rank_after'] == 's'
        assert payload['rank_exp'] == 99
        assert payload['rank_exp_after'] == 70

        context['game']['knockout'] = True
        obj.composite_result_udemae(context, payload)
        assert payload['knock_out'] == 'yes'

        context['game']['knockout'] = False
        obj.composite_result_udemae(context, payload)
        assert payload['knock_out'] == 'no'

    def test_composite_result_fest(self):
        return True

    def test_composite_screenshots(self):
        parent = StatInkMock()
        obj = _get_StatInkCompositor()(parent)

        payload = {}
        obj.composite_screenshots(payload)

        assert payload['image_result'] is not None
        assert payload['image_gear'] is not None
        assert payload['image_judge'] is not None

        payload = {}
        parent.img_scoreboard = None
        parent.img_judge = None
        parent.img_gears = None
        obj.composite_screenshots(payload)
        assert not ('image_result' in payload)
        assert not ('image_judge' in payload)
        assert not ('image_gears' in payload)
