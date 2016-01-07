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

import gettext

from datetime import datetime
import time

from ikalog.utils import *


# IkaLog Output Plugin: Show message on Console
#

t = gettext.translation('console', 'locale', fallback=True)
_ = t.gettext

class Console(object):

    ##
    # on_game_start Hook
    # @param self      The Object Pointer
    # @param context   IkaLog context
    #
    def on_game_start(self, context):
        map = IkaUtils.map2text(context['game']['map'])
        rule = IkaUtils.rule2text(context['game']['rule'])
        print(_('Game Start. Stage: %(stage)s Rule: %(rule)s') % {'rule': rule, 'stage':map})

    def on_game_killed(self, context):
        print(_('Splatted!'))

    def on_game_dead(self, context):
        print(_('You are splatted!'))

    def on_game_death_reason_identified(self, context):
        s = _('Cause of death: %(cause_of_death)s') % \
            { 'cause_of_death': context['game']['last_death_reason']}
        print(s)

    ##
    # Generate a message for on_game_individual_result.
    # @param self      The Object Pointer.
    # @param context   IkaLog context
    #
    def get_text_game_individual_result(self, context):
        map = IkaUtils.map2text(context['game']['map'])
        rule = IkaUtils.rule2text(context['game']['rule'])
        won = IkaUtils.getWinLoseText(
            context['game']['won'],
            win_text=_('won'),
            lose_text=_('lose'),
            unknown_text=_('unknown'),
        )
        t = datetime.now()
        t_str = t.strftime("%Y,%m,%d,%H,%M")
        t_unix = int(time.mktime(t.timetuple()))
        me = IkaUtils.getMyEntryFromContext(context)

        s = _('Game Result: Stage %(stage)s, Rule %(rule)s, Result %(result)s') % \
            {'rule': rule, 'stage':map, 'result': won}

        if ('score' in me):
            s = s + ' ' + _('%sp') % (s, me['score'])

        if ('kills' in me) and ('deaths' in me):
            try:
                s = s + ' ' + _('%dK/%dD') % (int(me['kills']), int(me['deaths']))
            except ValueError:
                pass

        if 'weapon' in me:
            s = s + ' ' + _('Weapon: %s') % (me['weapon'])

        if ('rank_in_team' in me):
            s = s + ' ' + _('Rank in the team: %s') % (me['rank_in_team'])

        if ('udemae_pre' in me) and me['udemae_pre']:
            s = s + ' ' + _('Rank: %s') % (me['udemae_pre'])

        return s

    ##
    # on_game_individual_result Hook
    # @param self      The Object Pointer
    # @param context   IkaLog context
    #
    def on_game_individual_result(self, context):
        s = self.get_text_game_individual_result(context)
        print(s)

    def on_game_session_end(self, context):
        print(_('Game Session end.'))
