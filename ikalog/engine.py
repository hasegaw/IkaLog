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

from __future__ import print_function

import cv2
import sys
import time
import traceback

from ikalog.utils import *
from . import scenes


# The IkaLog core engine.
#


class IkaEngine:
    scn_gamestart = scenes.GameStart()
    scn_gamefinish = scenes.GameFinish()
    scn_gameresult = scenes.ResultDetail()
    scn_result_udemae = scenes.ResultUdemae()
    scn_result_gears = scenes.ResultGears()
    scn_ingame = scenes.InGame()
    scn_tower_tracker = scenes.TowerTracker()
    scn_lobby = scenes.Lobby()

    last_capture = time.time() - 100
    last_gamestart = time.time() - 100
    last_lobby_matching = time.time() - 100
    last_lobby_matched = time.time() - 100

    def dprint(self, text):
        print(text, file=sys.stderr)

    def call_plugins(self, event_name, debug=False):
        if debug:
            self.dprint('call plug-in hook (%s):' % event_name)

        for op in self.output_plugins:
            if hasattr(op, event_name):
                if debug:
                    self.dprint('Call  %s' % op.__class__.__name__)
                try:
                    getattr(op, event_name)(self.context)
                except:
                    self.dprint('%s.%s() raised a exception >>>>' %
                                (op.__class__.__name__, event_name))
                    self.dprint(traceback.format_exc())
                    self.dprint('<<<<<')
            elif hasattr(op, 'onUncatchedEvent'):
                if debug:
                    self.dprint(
                        'call plug-in hook (UncatchedEvent, %s):' % event_name)
                try:
                    getattr(op, 'onUncatchedEvent')(event_name, self.context)
                except:
                    self.dprint('%s.%s() raised a exception >>>>' %
                                (op.__class__.__name__, event_name))
                    self.dprint(traceback.format_exc())
                    self.dprint('<<<<<')

    def stop(self):
        self._stop = True

    def reset(self):
        # Initalize the context
        self.context = {
            'game': {
                'map': None,
                'rule': None,
                'won': None,
                'players': None,
                'livesTrack': [],
                'towerTrack': [],
            },
            'engine': {
                'frame': None,
                'service': {
                    'callPlugins': self.call_plugins,
                }
            },
            'scenes': {
            },
            'config': {
            }
        }

    def process_frame(self):
        context = self.context

        skip_frames = 0
        if (self.capture.from_file and self.capture.fps > 28):
            skip_frames = int(self.capture.fps / 3)

        frame, t = self.read_next_frame(skip_frames=skip_frames)

        if frame is None:
            return False

        context['engine']['inGame'] = self.scn_ingame.matchTimerIcon(context)

        self.call_plugins('on_frame_read')

        self.scn_ingame.match(context)

        tower_data = self.scn_tower_tracker.match(context)

        try:
            # ライフをチェック
            (team1, team2) = self.scn_ingame.lives(context)
            # print("味方 %s 敵 %s" % (team1, team2))

            context['game']['livesTrack'].append(
                [context['engine']['msec'], team1, team2])
            if tower_data:
                context['game']['towerTrack'].append(
                    [context['engine']['msec'], tower_data.copy()])
        except:
            pass

        # Lobby
        r = False
        if not context['engine']['inGame']:
            r = self.scn_lobby.match(context)

        if r:
            if context['game']['lobby']['state'] == 'matching':
                if (time.time() - self.last_lobby_matching) > 60:
                    # マッチングを開始した
                    self.call_plugins('on_lobby_matching')
                self.last_lobby_matching = time.time()

            if context['game']['lobby']['state'] == 'matched':
                if (time.time() - self.last_lobby_matched) > 10:
                    # マッチングした直後
                    self.call_plugins('on_lobby_matched')
                self.last_lobby_matched = time.time()

        # GameStart (マップ名、ルール名が表示されている) ?

        r = None
        if (not context['engine']['inGame']) and (time.time() - self.last_gamestart) > 10:
            r = self.scn_gamestart.match(context)

        if r:
            context["game"] = {
                'map': None,
                'rule': None,
                'livesTrack': [],
                'towerTrack': [],
            }
            self.scn_tower_tracker.reset(context)

            while (r):
                frame, t = self.read_next_frame(skip_frames=3)
                r = self.scn_gamestart.match(context)

            self.last_gamestart = time.time()

            self.call_plugins('on_game_start')

        # GameFinish (ゲームが終了した) ?
        r = False
        if (not context['engine']['inGame']):
            r = self.scn_gamefinish.match(context)

        if r:
            self.call_plugins('on_game_finish')

        # GameResult (勝敗の詳細が表示されている）?
        r = (not context['engine']['inGame']) and (
            time.time() - self.last_capture) > 60
        if r:
            r = self.scn_gameresult.match(context)

        if r:
            if ((time.time() - self.last_capture) > 60):
                self.last_capture = time.time()

                # 安定するまで待つ
                for x in range(10):
                    frame, t = self.read_next_frame()

                # 安定した画像で再度解析
                self.scn_gameresult.analyze(context)

                self.call_plugins('on_game_individual_result_analyze')
                self.call_plugins('on_game_individual_result')

        # ResultUdemae
        r = (not context['engine']['inGame'])
        if r:
            r = self.scn_result_udemae.match(context)

        while r:
            frame, t = self.read_next_frame()
            r = self.scn_result_udemae.match(context)

        # result_gears
        r = (not context['engine']['inGame'])
        if r:
            r = self.scn_result_gears.match(context)
        if r:
            while r:
                frame, t = self.read_next_frame()
                r = self.scn_result_gears.match(context)

            self.call_plugins('on_game_session_end')
            self.call_plugins('on_game_reset')
            self.reset()

        key = None

        # FixMe: Since on_frame_next and on_key_press has non-standard arguments,
        # self.call_plugins() doesn't work for those.

        for op in self.output_plugins:
            if hasattr(op, "on_frame_next"):
                try:
                    key = op.on_frame_next(context)
                except:
                    pass

        for op in self.output_plugins:
            if hasattr(op, "on_key_press"):
                try:
                    op.on_key_press(context, key)
                except:
                    pass

    def read_next_frame(self, skip_frames=0):
        for i in range(skip_frames):
            frame, t = self.capture.read()
        frame, t = self.capture.read()

        while frame is None:
            self.call_plugins('on_frame_read_failed')
            if self._stop:
                return None, None
            cv2.waitKey(1000)
            frame, t = self.capture.read()

        self.context['engine']['msec'] = t
        self.context['engine']['frame'] = frame

        self.call_plugins('on_debug_read_next_frame')

        return frame, t

    def run(self):
        # Main loop.
        while not self._stop:
            if self._pause:
                time.sleep(0.5)
            else:
                self.process_frame()

        cv2.destroyAllWindows()

    def set_capture(self, capture):
        self.capture = capture

    def set_plugins(self, plugins):
        self.output_plugins = plugins

    def pause(self, pause):
        self._pause = pause

    def __init__(self):
        self._stop = False
        self._pause = True
        self.reset()
