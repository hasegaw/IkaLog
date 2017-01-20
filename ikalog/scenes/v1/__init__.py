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

def initialize_scenes(engine):
    import ikalog.scenes as scenes

    s = [
        scenes.GameTimerIcon(engine),
        scenes.GameStart(engine),
        scenes.GameGoSign(engine),
        scenes.GameKill(engine),
        scenes.GameKillCombo(engine),
        scenes.GameDead(engine),
        scenes.GameLowInk(engine),
        scenes.GameOutOfBound(engine),
        scenes.GameFinish(engine),
        scenes.GameSpecialGauge(engine),
        scenes.GameSpecialWeapon(engine),

        scenes.GameRankedBattleEvents(engine),
        scenes.PaintScoreTracker(engine),
        scenes.ObjectiveTracker(engine),
        scenes.SplatzoneTracker(engine),
        scenes.InklingsTracker(engine),

        scenes.ResultJudge(engine),
        scenes.ResultDetail(engine),
        scenes.ResultUdemae(engine),
        scenes.ResultGears(engine),
        scenes.ResultFesta(engine),

        scenes.Lobby(engine),
        # scenes.Downie(engine),

        scenes.Blank(engine),
    ]
    return s
