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

import sys
import numpy as np
import cv2
import time
import traceback

from IkaScene_GameStart import *
from IkaScene_ResultDetail import *
from IkaScene_TowerTracker import *
from IkaScene_InGame import *
from IkaScene_Lobby import *
from IkaScene_GameFinish import *


# The IkaLog core engine.
#
class IkaEngine:
    scn_gamestart = IkaScene_GameStart()
    scn_gamefinish = IkaScene_GameFinish()
    scn_gameresult = IkaScene_ResultDetail()
    scn_ingame = IkaScene_InGame()
    scn_towerTracker = IkaScene_TowerTracker()
    scn_lobby = IkaScene_Lobby()

    last_capture = time.time() - 100
    last_gamestart = time.time() - 100
    last_lobby_matching = time.time() - 100
    last_lobby_matched = time.time() - 100
    last_go_sign = time.time() - 100
    last_dead = time.time() - 100

    def dprint(self, text):
        print(text, file=sys.stderr)

    def callPlugins(self, event_name, debug=False):
        if debug:
            self.dprint("call plug-in hook (%s):" % event_name)
        for op in self.OutputPlugins:
            if hasattr(op, event_name):
                if debug:
                    self.dprint("Call  %s" % op.__class__.__name__)
                try:
                    getattr(op, event_name)(self.context)
                except:
                    self.dprint("%s.%s() raised a exception >>>>" %
                                (op.__class__.__name__, event_name))
                    self.dprint(traceback.format_exc())
                    self.dprint("<<<<<")

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
            },
            'config': {
            }
        }

    def processFrame(self):
        context = self.context  # Python のオブジェクトって参照だよね?
        frame = self.readNextFrame(skip_frames=12)
        # FixMe: frame can be a null

        context['engine']['frame'] = frame
        context['engine']['inGame'] = self.scn_ingame.matchTimerIcon(context)

        self.callPlugins('onFrameRead')

        if context['engine']['inGame']:
            # ゴーサイン
            r = False
            if self.last_go_sign + 60 < time.time():
                r = self.scn_ingame.matchGoSign(context)

            if r:
                self.last_go_sign = time.time()
                self.callPlugins('onGameGoSign')

            # 死亡状態（「復活まであとｎ秒」）
            if self.scn_ingame.matchDead(context):
                if self.last_dead + 3 < time.time():
                    self.callPlugins('onGameDead')
                self.last_dead = time.time()

            tower_data = self.scn_towerTracker.match(context)

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
                    self.callPlugins('onLobbyMatching')
                self.last_lobby_matching = time.time()

            if context['game']['lobby']['state'] == 'matched':
                if (time.time() - self.last_lobby_matched) > 10:
                    # マッチングした直後
                    self.callPlugins('onLobbyMatched')
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
            self.scn_towerTracker.reset(context)

            while (r):
                frame = self.readNextFrame(skip_frames=3)
                context['engine']['frame'] = frame
                r = self.scn_gamestart.match(context)

            self.last_gamestart = time.time()

            self.callPlugins('onGameStart')

        # GameFinish (ゲームが終了した) ?
        r = False
        if (not context['engine']['inGame']):
            r = self.scn_gamefinish.match(context)

        if r:
            self.callPlugins('onGameFinish')

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
                    frame = self.readNextFrame()

                # 安定した画像で再度解析
                context['engine']['frame'] = frame
                self.scn_gameresult.analyze(context)

                self.callPlugins('onGameIndividualResultAnalyze')
                self.callPlugins('onGameIndividualResult')
                self.callPlugins('onGameReset')

                self.reset()

        key = None

        # FixMe: Since onFrameNext and onKeyPress has non-standard arguments,
        # self.callPlugins() doesn't work for those.

        for op in self.OutputPlugins:
            if hasattr(op, "onFrameNext"):
                try:
                    key = op.onFrameNext(context)
                except:
                    pass

        for op in self.OutputPlugins:
            if hasattr(op, "onKeyPress"):
                try:
                    op.onKeyPress(context, key)
                except:
                    pass

    def readNextFrame(self, skip_frames=0):
        for i in range(skip_frames):
            frame, t = self.capture.read()
        frame, t = self.capture.read()

        while frame is None:
            self.callPlugins('onFrameReadFailed')
            if self._stop:
                return None, None
            cv2.waitKey(1000)
            frame, t = self.capture.read()

        self.context['engine']['msec'] = t
        return frame

    def run(self):
        # Main loop.
        while not self._stop:
            if self._pause:
                time.sleep(0.5)
            else:
                self.processFrame()

        cv2.destroyAllWindows()

    def setCapture(self, capture):
        self.capture = capture

    def setPlugins(self, plugins):
        self.OutputPlugins = plugins

    def pause(self, pause):
        self._pause = pause

    def __init__(self):
        self._stop = False
        self._pause = True
        self.reset()

if __name__ == "__main__":
    from IkaConfig import *
    _capture, _OutputPlugins = IkaConfig().config()
    engine = IkaEngine()
    engine.pause(False)
    engine.setCapture(_capture)
    engine.setPlugins(_OutputPlugins)
    engine.run()
