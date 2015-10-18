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

from test.scenes.scene_test import SceneTestCase

class TestLobby(SceneTestCase):

    scene_name = 'lobby'

    def noop(self, context):
        pass

    def _load_scene_class(self):
        from ikalog.scenes.lobby import Lobby
        return Lobby(None)

    def _test_scene(self, filename, lobby_type=None, state=None):
        frame = self._load_screenshot(filename)
        obj = self._load_scene_class()

        context = {
            'engine': {'frame': frame, 'msec': 0,
                'service': { 'callPlugins': self.noop} },
            'game': {},
            'scenes': {},
            'lobby': {},
        }

        assert(obj.match(context))

        context_scene = context['lobby']

        if lobby_type is not None:
            assert(context_scene['type'] == lobby_type)

        if state is not None:
            assert(context_scene['state'] == state)

        return obj, context

    def test_lobby_fes_matched(self):
        self._test_scene(
            'lobby_fes_matched.png',
            lobby_type='festa',
            state='matched',
        )

    def test_lobby_fes_matching(self):
        self._test_scene(
            'lobby_fes_matching.png',
            lobby_type='festa',
            state='matching',
        )

    def test_lobby_public_ranked_matched(self):
        self._test_scene(
            'lobby_public_ranked_matched.png',
            lobby_type='public',
            state='matched',
        )

    def test_lobby_public_ranked_matching(self):
        self._test_scene(
            'lobby_public_ranked_matching.png',
            lobby_type='public',
            state='matching',
        )

    def test_lobby_public_turf_matched(self):
        self._test_scene(
            'lobby_public_turf_matched.png',
            lobby_type='public',
            state='matched',
        )

    def test_lobby_public_turf_matched_cv710(self):
        # AVerMedia CV710 capture
        self._test_scene(
            'lobby_nawabari_matched_cv710.png',
            lobby_type='public',
            state='matched',
        )

    def test_lobby_public_turf_matching(self):
        self._test_scene(
            'lobby_public_turf_matching.png',
            lobby_type='public',
            state='matching',
        )

    def test_lobby_tag_2_matched(self):
        self._test_scene(
            'lobby_tag_2_matched.png',
            lobby_type='tag',
            state='matched',
        )

    def test_lobby_tag_2_matching(self):
        self._test_scene(
            'lobby_tag_2_matching.png',
            lobby_type='tag',
            state='matching',
        )

    def test_lobby_tag_4_matched(self):
        self._test_scene(
            'lobby_tag_4_matched.png',
            lobby_type='tag',
            state='matched',
        )

    def test_looby_private_matching(self):
        self._test_scene(
            'lobby_private_matching.1.png',
            lobby_type='private',
            state='matching',
        )

    def test_looby_private_matched(self):
        self._test_scene(
            'lobby_private_matched.1.png',
            lobby_type='private',
            state='matched',
        )
