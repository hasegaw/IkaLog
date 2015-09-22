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

from IkaUtils import *
from datetime import datetime
import time

# IkaLog Output Plugin: Show message on Console
#


class IkaOutput_Console:

    ##
    # onGameStart Hook
    # @param self      The Object Pointer
    # @param context   IkaLog context
    #
    def onGameStart(self, context):
        map = IkaUtils.map2text(context['game']['map'])
        rule = IkaUtils.rule2text(context['game']['rule'])
        print("ゲームスタート。マップ %s ルール %s" % (map, rule))

    ##
    # Generate a message for onGameIndividualResult.
    # @param self      The Object Pointer.
    # @param context   IkaLog context
    #
    def getTextGameIndividualResult(self, context):
        map = IkaUtils.map2text(context['game']['map'])
        rule = IkaUtils.rule2text(context['game']['rule'])
        won = IkaUtils.getWinLoseText(
            context['game']['won'], win_text="勝ち", lose_text="負け", unknown_text="不明")
        t = datetime.now()
        t_str = t.strftime("%Y,%m,%d,%H,%M")
        t_unix = int(time.mktime(t.timetuple()))
        me = IkaUtils.getMyEntryFromContext(context)

        s = 'ゲーム終了。'
        s = '%s ステージ:%s' % (s, map)
        s = '%s ルール:%s' % (s, rule)

        if ('kills' in me) and ('deaths' in me):
            s = '%s %dK/%dD' % (s, me['kills'], me['deaths'])

        if 'weapon' in me:
            s = '%s 使用ブキ:%s' % (s, me['weapon'])

        if ('rank_in_team' in me):
            s = '%s チーム内順位: %d' % (s, me['rank_in_team'])

        return s

    ##
    # onGameIndividualResult Hook
    # @param self      The Object Pointer
    # @param context   IkaLog context
    #
    def onGameIndividualResult(self, context):
        s = self.getTextGameIndividualResult(context)
        print(s)
