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

from test.scenes.scene_test import SceneTestCase
from ikalog.utils import IkaUtils


class TestGameSession(unittest.TestCase):
    scene_name = 'GameSession'

    def _load_scene_class(self):
        from ikalog.scenes import GameSession
        return GameSession(None)

    def test_timeout(self):
        from ikalog.engine import IkaEngine

        engine = IkaEngine()
        game_session = engine.find_scene_object('GameSession')
        context = engine.context

        # on_game_start() changes the state to ST_GAME_OPENING,
        # and set timeout.
        game_session.on_game_start(context)

        self.assertEqual(game_session.ST_GAME_OPENING, game_session._state)
        self.assertNotEqual(None, game_session._next_timeout)

        context['engine']['msec'] = 1000

        game_session._set_timeout(context, msec_rel=500)
        self.assertEqual(1500, game_session._next_timeout)

        game_session._set_timeout(context, msec=2000)
        self.assertEqual(2000, game_session._next_timeout)

        # At t=1000ms, timeout=2000 won't be triggered yet.
        self.assertEqual(False, game_session._check_timeout(context))

        # At t=3000ms, timeout=2000 will be triggered.
        # _next_timeout will be cleared.
        context['engine']['msec'] = 3000

        self.assertEqual(True, game_session._check_timeout(context))

        # Cause timeout.
        # State will be ST_NONE, and the timeout will be updated to None.

        game_session._timeout()
        self.assertEqual(game_session.ST_NONE, game_session._state)
        self.assertEqual(None, game_session._next_timeout)

        # At t=4000ms, timeout=2000 will not be triggered,
        # bacause state == ST_NONE
        context['engine']['msec'] = 4000

        self.assertEqual(False, game_session._check_timeout(context))

    def test_game_index(self):
        from ikalog.engine import IkaEngine

        engine = IkaEngine()
        game_session = engine.find_scene_object('GameSession')
        context = engine.context

        assert game_session

        # Index should start at 0.
        self.assertEqual(0, context['game']['index'])

        # Set index to 3. It should be incremented even engine reset.
        context['game']['index'] = 3

        self.assertEqual(3, context['game']['index'])  # Obiously True.

        engine.reset()
        self.assertEqual(3, context['game']['index'])  # Still True.

        engine.reset()
        self.assertEqual(3, context['game']['index'])  # Still True :-)

        # State doesn't get update by on_lobby_matched()
        # got triggered. In this situation, close_session() will
        # close the game, and increment the index.

        game_session.on_lobby_matched(context)  # -> ST_NONE
        self.assertEqual(game_session.ST_NONE, game_session._state)

        # State will be ST_GAME_CLOSING when on_game_individual_result()
        # got triggered. In this situation, close_session() will
        # close the game, and increment the index.

        game_session.on_game_individual_result(context)  # -> ST_GAME_CLOSING
        self.assertEqual(game_session.ST_GAME_CLOSING, game_session._state)

        game_session.close_session(context)  # -> close
        game_session.game_reset(context)

        self.assertEqual(4, context['game']['index'])

        # State will be ST_GAME_OPENING when on_game_start()
        # got triggered. In this situation, close_session() will
        # abort the game, and also increment the index.

        game_session.on_game_start(context)  # -> ST_GAME_OPENING
        self.assertEqual(game_session.ST_GAME_OPENING, game_session._state)

        game_session.close_session(context)  # -> abort
        game_session.game_reset(context)

        self.assertEqual(5, context['game']['index'])
