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


def _get_class():
    from ikalog.outputs.csv import CSVPlugin
    return CSVPlugin


class TestCSVPlugin(unittest.TestCase):

    def test_result_scoreboard2test(self):
        from ikalog.outputs.csv import CSVPlugin, _result_scoreboard2text
        obj = _get_class()()
        context = {'game': {}}
        context['game']['map'] = 'arowana'
        context['game']['rule'] = 'hoko'
        context['game']['won'] = True
        s = _result_scoreboard2text(context).split(',')
        assert 'Arowana Mall' in s
        assert 'Rainmaker' in s
        assert '勝ち\n' in s

        context['game']['won'] = False
        s = _result_scoreboard2text(context).split(',')
        assert '負け\n' in s

        # Should not raise exception without context['game']['won']
        del context['game']['won']
        s = _result_scoreboard2text(context)

    def test_append_file(self):
        # FIXME: temp_filename should be generated automatically
        temp_filename = '/tmp/hoge'

        assert not os.path.exists(temp_filename)

        from ikalog.outputs.csv import _append_file

        # Test the function
        _append_file(temp_filename, 'hello worrld')
        assert os.path.exists(temp_filename)

        s = open(temp_filename, 'r').read()
        assert s.startswith('hello')

        # Remove the temp file
        os.remove(temp_filename)
        assert not os.path.exists(temp_filename)

    def test_config(self):
        from ikalog.outputs.csv import CSVPlugin
        obj = CSVPlugin()
        config = {'enabled': True, 'filename': 'bubi'}
        obj.set_configuration(config)

    def test_event_handler(self):
        # FIXME: temp_filename should be generated automatically
        temp_filename = '/tmp/hoge'

        from ikalog.outputs.csv import CSVPlugin
        obj = CSVPlugin()

        context = {'game': {
            'map': 'arowana', 'rule': 'hoko', 'won': True,
        }}

        obj.set_configuration({'enabled': False, 'filename': '/not/exist'})
        obj.on_game_session_end(context)  # enabled -> False

        obj.set_configuration({'enabled': False, 'filename': temp_filename})
        obj.on_game_session_end(context)
        assert not os.path.exists(temp_filename)

        obj.set_configuration({'enabled': True, 'filename': temp_filename})
        obj.on_game_session_end(context)
        assert os.path.exists(temp_filename)

        # Remove the temp file
        os.remove(temp_filename)
        assert not os.path.exists(temp_filename)


if __name__ == '__main__':
    unittest.main()
