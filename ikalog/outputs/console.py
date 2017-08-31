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

from datetime import datetime
import time

from ikalog.utils import *


# IkaLog Output Plugin: Show message on Console
#

_ = Localization.gettext_translation('console', fallback=True).gettext


class Console(object):

    ##
    # on_game_start Hook
    # @param self      The Object Pointer
    # @param context   IkaLog context
    #
    def on_game_start(self, context):
        stage = IkaUtils.map2text(context['game']['map'])
        rule = IkaUtils.rule2text(context['game']['rule'])
        print(_('Game Start. Stage: %(stage)s, Mode: %(rule)s') %
              {'rule': rule, 'stage': stage})

    def on_game_killed(self, context, params):
        print(_('Splatted an enemy! (%(streak)d streak)') %
              {'streak': context['game'].get('kill_streak', 1)})

    def on_game_chained_kill_combo(self, context):
        print(_('You chained %(combo)d kill combo(s)!') %
              {'combo': context['game'].get('kill_combo', 1)})

    def on_game_dead(self, context):
        print(_('You were splatted!'))

    def on_game_special_weapon(self, context):
        s = '%s, mine == %s' % (
            context['game']['special_weapon'], context['game']['special_weapon_is_mine'])
        print(_('Special Weapon Activation: %s' % s))

    def on_game_death_reason_identified(self, context):
        s = _('Cause of death: %(cause_of_death)s') % \
            {'cause_of_death': context['game']['last_death_reason']}
        print(s)

    def on_game_go_sign(self, context):  # "Go!"
        print(_('Go!'))

    def on_game_finish(self, context):  # Finish tape
        print(_('Game End.'))

    # Ranked battle common events

    def on_game_ranked_we_lead(self, context):
        print(_('We\'ve taken the lead!'))

    def on_game_ranked_they_lead(self, context):
        print(_('We lost the lead!'))

    # Ranked, Splat Zone battles

    def on_game_splatzone_we_got(self, context):
        print(_('We\'re in control!'))

    def on_game_splatzone_we_lost(self, context):
        print(_('We lost control!'))

    def on_game_splatzone_they_got(self, context):
        print(_('They\'re in control!'))

    def on_game_splatzone_they_lost(self, context):
        print(_('They lost control!'))

    # Ranked, Rainmaker battles

    def on_game_rainmaker_we_got(self, context):
        print(_('We have the Rainmaker!'))

    def on_game_rainmaker_we_lost(self, context):
        print(_('We lost the Rainmaker!'))

    def on_game_rainmaker_they_got(self, context):
        print(_('They have the Rainmaker!'))

    def on_game_rainmaker_they_lost(self, context):
        print(_('They lost the Rainmaker!'))

    # Ranked, Tower Control battles

    def on_game_tower_we_got(self, context):
        print(_('We took the tower!'))

    def on_game_tower_we_lost(self, context):
        print(_('We lost the tower!'))

    def on_game_tower_they_got(self, context):
        print(_('They took the tower!'))

    def on_game_tower_they_lost(self, context):
        print(_('They lost the tower!'))

    ##
    # Salmon Run events

    def on_salmonrun_game_start(self, context, params):
        print(_('Salmon Run Start. stage: %s') % params['stage'])

    def on_salmonrun_weapon_specified(self, context):
        print(_('You gotta new weapon!'))

    def on_salmonrun_norma_reached(self, context):
        print(_('Your team reached the norma of this wave!'))

    def on_salmonrun_result_judge(self, context):
        print(_('Work result: %s') % context['salmon_run']['result'])

    def on_salmonrun_wave_start(self, context, params):
        print(_('Wave %s start...') % params['wave'])

    def on_salmonrun_egg_captured(self, context, params):
        print(_('Player %d captured an egg') % params['player'])

    def on_salmonrun_egg_delivered(self, context, params):
        print(_('Player %d delivered an egg') % params['player'])

    def on_salmonrun_egg_delivered(self, context, params):
        print(_('Player %d delivered an egg') % params['player'])

    def on_salmonrun_player_dead(self, context, params):
        print(_('Player %d is now dead') % params['player'])

    def on_salmonrun_player_back(self, context, params):
        print(_('Player %d is now back') % params['player'])

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
        me = IkaUtils.getMyEntryFromContext(context)

        s = _('Results. Stage: %(stage)s, Mode: %(rule)s, Result: %(result)s') % \
            {'rule': rule, 'stage': map, 'result': won}

        if ('score' in me):
            s = s + ' ' + _('%sp') % (me['score'])

        if ('kills' in me) and ('deaths' in me):
            try:
                s = s + ' ' + \
                    _('%dK/%dD') % (int(me['kills']), int(me['deaths']))
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
