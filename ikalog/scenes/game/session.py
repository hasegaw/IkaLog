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

import sys

import cv2

from ikalog.scenes.stateful_scene import StatefulScene
from ikalog.utils import IkaUtils


class GameSession(StatefulScene):
    """
    Game Session Manager.
    """

    def _timeout(self):
        self._next_timeout = None
        self._switch_state(self.ST_NONE)

    def _set_timeout(self, context, msec_rel=None, msec=None):
        # assert (msec_rel and msec) or not (msec_rel or msec), 'msec_rel %s msec %s' % (msec_rel, msec)

        if msec_rel:
            self._next_timeout = (context['engine']['msec'] or 0) + msec_rel
        else:
            self._next_timeout = msec

    def _check_timeout(self, context):
        return (self._state != self._state_default) and self._next_timeout \
            and (self._next_timeout < context['engine']['msec'])

    def _session_abort(self, context):
        if self._state == self.ST_NONE:
            # Not applicable.
            return False

        if not context['game']['end_time']:
            # end_time should be initialized in GameFinish or session_close.
            # This is a fallback in case they were skipped.
            context['game']['end_time'] = IkaUtils.getTime(context)
            context['game']['end_offset_msec'] = context['engine']['msec']

        context['engine']['engine'].call_plugins_later('on_game_lost_synnc')
        context['engine']['engine'].call_plugins_later('on_game_session_abort')
        context['engine']['engine'].call_plugins_later('on_game_pre_reset')
        self._timeout()
        return True

    def _session_close(self, context):
        if self._state == self.ST_NONE:
            # Not applicable.
            return False

        if not context['game']['end_time']:
            # end_time should be initialized in GameFinish.
            # This is a fallback in case GameFinish was skipped.
            context['game']['end_time'] = IkaUtils.getTime(context)
            context['game']['end_offset_msec'] = context['engine']['msec']

        context['engine']['engine'].call_plugins_later('on_game_session_end')
        context['engine']['engine'].call_plugins_later('on_game_pre_reset')
        self._timeout()
        return True

    def game_reset(self, context):
        IkaUtils.dprint('%s: Resetting game information' % self)
        index = context.get('game', {}).get('index', 0)

        if 'game' in context:
            # Increment the value only when end_time is available,
            # (e.g. the game was finished).
            if context['game'].get('end_time'):
                index += 1

        # Initalize the context
        context['game'] = {
            # Index of this game.
            'index': index,

            'map': None,
            'rule': None,
            'won': None,
            'players': None,

            'kills': 0,
            'dead': False,
            'death_reasons': {},

            'inkling_state': [None, None],

            # Float values of start and end times scince the epoch in second.
            # They are used with IkaUtils.GetTime.
            'start_time': None,
            'end_time': None,
            # Int values of start and end offset times in millisecond.
            # They are used with context['engine']['msec']
            'start_offset_msec': None,
            'end_offset_msec': None,
        }
        self._call_plugins('on_game_reset')

    def close_session(self, context):
        """
        Close the current session now.

        If the state is ST_NONE, nothing happens.
        If the state is not ST_GAME_CLOSING, the game will be aborted instead.
        """

        if self._state == self.ST_GAME_CLOSING:
            return self._session_close(context)
        else:
            return self._session_abort(context)

    def abort_session(self, context):
        """
        Abort the current session now.

        If the state is ST_NONE, nothing happens.
        """
        return self._session_abort(context)

    def state(self):
        """
        Get current state.

        Return value should be one of [ST_NONE, ST_GAME_OPENING, ST_IN_GAME, ST_GAME_CLOSING]
        """
        return self._state

    # override
    def reset(self):
        super(GameSession, self).reset()
        self._switch_state(self.ST_NONE)
        self._timeout()

    # Handlers

    def on_lobby_matching(self, context):
        self._switch_state(self.ST_NONE)

    def on_lobby_matched(self, context):
        self._switch_state(self.ST_NONE)

    def on_game_start(self, context):
        self._switch_state(self.ST_GAME_OPENING)
        self._set_timeout(context, msec_rel=30 * 1000)

    def on_game_go_sign(self, context):
        self._switch_state(self.ST_IN_GAME)
        self._set_timeout(context, msec_rel=30 * 1000)

    def on_game_finish(self, context):
        self._switch_state(self.ST_GAME_CLOSING)
        self._set_timeout(context, msec_rel=60 * 1000)

    def on_result_judge(self, context):
        self._switch_state(self.ST_GAME_CLOSING)
        self._set_timeout(context, msec_rel=30 * 1000)

    def on_game_individual_result(self, context):
        self._switch_state(self.ST_GAME_CLOSING)
        self._set_timeout(context, msec_rel=20 * 1000)

    def on_result_gears(self, context):
        self._switch_state(self.ST_GAME_CLOSING)
        self._set_timeout(context, msec_rel=1 * 1000)

    # state handlers

    def _state_default(self, context):
        if self.is_another_scene_matched(context, 'GameTimerIcon'):
            self._switch_state(self.ST_IN_GAME)
            self._set_timeout(context, msec_rel=30 * 1000)
            return True

        return False

    def _state_opening(self, context):
        if self.is_another_scene_matched(context, 'GameTimerIcon'):
            self._switch_state(self.ST_IN_GAME)
            self._set_timeout(context, msec_rel=30 * 1000)
            return True

        if self._check_timeout(context):
            self._session_abort(context)
            return False

        # chain to default state handler.
        return True

    def _state_in_game(self, context):
        if self.is_another_scene_matched(context, 'GameTimerIcon'):
            self._set_timeout(context, msec_rel=30 * 1000)
            return True

        if self._check_timeout(context):
            print('_state_in_game: timeout, aborting',
                  self._next_timeout, context['engine']['msec'])
            self._session_abort(context)
            return False

        return True

    def _state_closing(self, context):
        if self._check_timeout(context):
            print('_state_closing: timeout, aborting',
                  self._next_timeout, context['engine']['msec'])
            self._session_close(context)
            return False

        return True

    def dump(self, context):
        pass

    def _analyze(self, context):
        pass

    def _init_scene(self, debug=False):
        pass

    ST_NONE = _state_default
    ST_GAME_OPENING = _state_opening
    ST_GAME_CLOSING = _state_closing
    ST_IN_GAME = _state_in_game
if __name__ == "__main__":
    GameSession.main_func()
