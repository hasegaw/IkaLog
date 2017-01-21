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

from .game.respawn import V2GameRespawn as GameRespawn
from .game.special_gauge.background import V2GameSpecialGaugeBackground as GameSpecialGaugeBackground
from .game.special_gauge.gauge import V2GameSpecialGauge as GameSpecialGauge
from .game.special_gauge.level import V2GameSpecialGaugeLevel as GameSpecialGaugeLevel
from .game.special_gauge.sub_and_special import V2GameSubAndSpecial as GameSubAndSpecial
from .game.superjump import V2GameSuperJump as GameSuperJump
from .game.kill import V2GameKill as GameKill

from .result.judge import V2ResultJudge as ResultJudge
from .result.scoreboard.scoreboard import V2ResultScoreboard as ResultScoreboard

def initialize_scenes(engine):
    import ikalog.scenes as scenes

    s = [
        scenes.GameTimerIcon(engine),

        GameRespawn(engine),

        GameSpecialGauge(engine),
        GameSpecialGaugeBackground(engine),
        GameSpecialGaugeLevel(engine),
        GameSubAndSpecial(engine),

        GameSuperJump(engine),
        GameKill(engine),

        ResultJudge(engine),
        ResultScoreboard(engine),

        scenes.Blank(engine),
    ]
    return s
