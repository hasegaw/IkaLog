#!/usr/bin/env python3
# -*- coding: utf-8 -*-
#
#  IkaLog
#  ======
#  Copyright (C) 2017 Takeshi HASEGAWA
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
import time
import unittest


class TestScreenshotPlugin(unittest.TestCase):

    def test_plugin(self):
        from ikalog.outputs.videorecorder import VideoRecorderPlugin
        obj = VideoRecorderPlugin()
        assert obj.get_configuration()['enabled'] == False

        conf = {
            'enabled': True,
            'dest_dir': '/tmp',
            'auto_rename': False,
            'script_name': 'test/outputs/videorecorder_mock_script.sh',
        }
        obj.set_configuration(conf)
        assert obj.get_configuration()['enabled'] == True

    def test_set_basic_variables(self):
        from ikalog.outputs.videorecorder import VideoRecorderPlugin
        obj = VideoRecorderPlugin()

        context = {
            'game': {
                'map': 'arowana',
                'rule': 'hoko',
                'won': True,
            }
        }

        vars_list = ['IKALOG_STAGE', 'IKALOG_RULE', 'IKALOG_WON']
        for v in vars_list:
            if v in os.environ:
                del os.environ[v]
            assert not (v in os.environ)

        obj.set_basic_variables(context)

        for v in vars_list:
            assert v in os.environ

    def _run_external_script_mock(self, s):
        self._last_external_script_arg = s
        raise Exception(s)

    def test_run_xxx(self):
        from ikalog.outputs.videorecorder import VideoRecorderPlugin
        obj = VideoRecorderPlugin()

        obj.run_external_script = self._run_external_script_mock

        try:
            obj.run_stop()
            assert False
        except Exception as e:
            assert e.args[0] == 'stop'

        try:
            obj.run_start()
            assert False
        except Exception as e:
            assert e.args[0] == 'start'

        try:
            obj.run_test()
            assert False
        except Exception as e:
            assert e.args[0] == 'test'

    def test_on_lobby_matched(self):
        from ikalog.outputs.videorecorder import VideoRecorderPlugin
        obj = VideoRecorderPlugin()
        obj.run_external_script = self._run_external_script_mock

        assert obj.get_configuration()['enabled'] == False

        context = {}
        obj.on_lobby_matched(context)

        obj.config['enabled'] = True
        try:
            obj.on_lobby_matched(context)
            raise Exception()
        except Exception as e:
            assert e.args[0] == 'start'

    def test_on_result_scoreboard(self):
        from ikalog.outputs.videorecorder import VideoRecorderPlugin
        obj = VideoRecorderPlugin()
        obj.run_external_script = self._run_external_script_mock

        assert obj.get_configuration()['enabled'] == False

        context = {
            'game': {
                'map': 'arowana',
                'rule': 'hoko',
                'won': True,
            }
        }
        obj.on_game_individual_result(context)

        obj.config['enabled'] = True
        obj.on_game_individual_result(context)

        time.sleep(1)
        assert self._last_external_script_arg == 'stop'

        assert 'IKALOG_WON' in os.environ
        assert not 'IKALOG_MP4_DESTDIR' in os.environ
        assert not 'IKALOG_MP4_DESTNAME' in os.environ

    def test_on_result_scoreboard_rename(self):
        from ikalog.outputs.videorecorder import VideoRecorderPlugin
        obj = VideoRecorderPlugin()
        obj.run_external_script = self._run_external_script_mock

        context = {
            'game': {
                'map': 'arowana',
                'rule': 'hoko',
                'won': True,
            }
        }

        obj.config['enabled'] = True
        obj.config['auto_rename'] = True
        obj.config['dest_dir'] = '/tmp/'
        obj.on_game_individual_result(context)

        time.sleep(1)
        assert self._last_external_script_arg == 'stop'

        assert 'IKALOG_WON' in os.environ
        assert 'IKALOG_MP4_DESTDIR' in os.environ
        assert 'IKALOG_MP4_DESTNAME' in os.environ

        for k in ['IKALOG_MP4_DESTDIR', 'IKALOG_MP4_DESTNAME']:
            print(os.environ[k])
