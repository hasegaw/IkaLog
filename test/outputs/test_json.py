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


class TestCSVPlugin(unittest.TestCase):

    def test_result_scoreboard2json_game(self):
        from ikalog.outputs.printjson import _result_scoreboard2json_game

        context = {
            'game': {
                'map': 'arowana',
                'rule': 'hoko',
                'won': True
            },
            'scenes': {
            }
        }
        record = _result_scoreboard2json_game(context)

        assert record['map'] == 'arowana'
        assert record['rule'] == 'hoko'
        assert record['result'] == 'win'

        context['game']['won'] = False
        record = _result_scoreboard2json_game(context)
        assert record['result'] == 'lose'

        context['scenes'] = {'result_gears': {'cash': 12345}}
        record = _result_scoreboard2json_game(context)
        assert record['cash_after'] == 12345

    def test_result_scoreboard2json_lobby(self):
        from ikalog.outputs.printjson import _result_scoreboard2json_lobby

        context = {
            'lobby': {
                'type': 'nawabari',
            }
        }
        record = {}
        _result_scoreboard2json_lobby(context, record)
        assert record['lobby'] == 'nawabari'

        context = {}
        record = {}
        _result_scoreboard2json_lobby(context, record)
        # No expection

    def test_result_scoreboard2json_ranked_battle(self):
        from ikalog.outputs.printjson import _result_scoreboard2json_ranked_battle
        context = {'game': {
            'result_udemae_str_pre': 'S',
            'result_udemae_exp_pre': 50,
            'result_udemae_str': 'S+',
            'result_udemae_exp': 80,
        }}

        record = {}
        _result_scoreboard2json_ranked_battle(context, record)
        assert record['udemae_pre'] == 'S'
        assert record['udemae_exp_pre'] == 50
        assert record['udemae_after'] == 'S+'
        assert record['udemae_exp_after'] == 80

    def test_result_scoreboard2json_players(self):
        from ikalog.outputs.printjson import _result_scoreboard2json_players
        context = {
            'game': {
                'players': [
                    {
                        'weapon': 'dualsweeper',
                        'kills': 10,
                        'deaths': 5,
                        'me': True,
                    },
                    {
                        'weapon': 'dynamo',
                    },
                ],
            },
        }

        record = {}
        _result_scoreboard2json_players(context, record)
        print(record)

        assert record['players'][0]['weapon'] == 'dualsweeper'
        assert record['players'][0]['kills'] == 10
        assert record['players'][0]['deaths'] == 5
        assert record['players'][1]['weapon'] == 'dynamo'

    def test_append_file(self):
        # FIXME: temp_filename should be generated automatically
        temp_filename = '/tmp/hoge'

        assert not os.path.exists(temp_filename)

        from ikalog.outputs.printjson import _append_file

        # Test the function
        _append_file(temp_filename, 'hello worrld')
        assert os.path.exists(temp_filename)

        s = open(temp_filename, 'r').read()
        assert s.startswith('hello')

        # Remove the temp file
        os.remove(temp_filename)
        assert not os.path.exists(temp_filename)

    def test_config(self):
        from ikalog.outputs.printjson import JSONPlugin
        obj = JSONPlugin()
        config = {'enabled': True, 'filename': 'bubi'}
        obj.set_configuration(config)

    def test_event_handler(self):
        # FIXME: temp_filename should be generated automatically
        temp_filename = '/tmp/hoge'

        from ikalog.outputs.printjson import JSONPlugin
        obj = JSONPlugin()

        context = {
            'game': {
                'map': 'arowana',
                'rule': 'hoko',
                'won': True
            },
            'scenes': {
            }
        }

        obj.set_configuration({'enabled': False, 'filename': '/not/exist'})
        obj.on_game_go_sign(context)
        obj.on_game_session_end(context)  # enabled -> False

        obj.set_configuration({'enabled': False, 'filename': temp_filename})
        obj.on_game_go_sign(context)
        obj.on_game_session_end(context)
        assert not os.path.exists(temp_filename)

        obj.set_configuration({'enabled': True, 'filename': temp_filename})
        obj.on_game_go_sign(context)
        obj.on_game_session_end(context)
        assert os.path.exists(temp_filename)

        # Remove the temp file
        os.remove(temp_filename)
        assert not os.path.exists(temp_filename)


if __name__ == '__main__':
    unittest.main()
