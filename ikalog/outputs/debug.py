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
import os
import sys
import time

from ikalog.utils import *


# IkaLog Output Plugin: Write debug logs.


class DebugLog(object):

    def write_debug_log(self, event, context, text=''):
        gt = int(context['engine']['msec'] / 1000)
        mm = '{0:02d}'.format(int(gt / 60))
        ss = '{0:02d}'.format(int(gt % 60))

        # Write to console
        print('[event] %s:%s %s  %s' % (mm, ss, event, text))

        # Write to screenshot if enabled
        if self.screenshot:
            t = time.localtime()
            time_str = time.strftime("%Y%m%d_%H%M%S", t)
            log_name = '%s_%s_%s.png' % (event, time_str, time.time())
            destfile = os.path.join(self.dir, log_name)
            IkaUtils.writeScreenshot(destfile, context['engine']['frame'])

    def on_frame_read_failed(self, context):
        pass

    # In-game typical events

    def on_game_killed(self, context, params):
        self.write_debug_log(sys._getframe().f_code.co_name, context)

    def on_game_chained_kill_combo(self, context):
        self.write_debug_log(sys._getframe().f_code.co_name, context)

    def on_game_dead(self, context):
        self.write_debug_log(sys._getframe().f_code.co_name, context)

    def on_game_death_reason_identified(self, context):
        s = "weapon = %s" % (context['game']['last_death_reason'])
        self.write_debug_log(sys._getframe().f_code.co_name, context, text=s)

    def on_game_low_ink(self, context):
        self.write_debug_log(sys._getframe().f_code.co_name, context,
            text="count=%d" % context['game']['low_ink_count'])

    def on_game_inkling_state_update(self, context):
        self.write_debug_log(sys._getframe().f_code.co_name, context,
                             text=str(context['game']['inkling_state']))

    def on_game_go_sign(self, context):
        self.write_debug_log(sys._getframe().f_code.co_name, context)

    def on_game_start(self, context):
        self.write_debug_log(sys._getframe().f_code.co_name, context)

    def on_game_team_color(self, context):
        self.write_debug_log(sys._getframe().f_code.co_name, context)

    def on_lobby_matching(self, context):
        s = 'Lobby_type: %s' % context['lobby']['type']

        self.write_debug_log(sys._getframe().f_code.co_name, context,
                             text=s)

    def on_lobby_matched(self, context):
        s = 'Lobby_type: %s' % context['lobby']['type']

        if context['lobby']['type'] == 'tag':
            s = s + ', team_members: %d' % context['lobby']['team_members']

        self.write_debug_log(sys._getframe().f_code.co_name, context,
                             text=s)

    def on_game_finish(self, context):
        self.write_debug_log(sys._getframe().f_code.co_name, context)

    # Common events to ranked battles.

    def on_game_ranked_we_lead(self, context):
        self.write_debug_log(sys._getframe().f_code.co_name, context)

    def on_game_ranked_they_lead(self, context):
        self.write_debug_log(sys._getframe().f_code.co_name, context)

    # Ranked, Splatzone battles

    def on_game_splatzone_we_got(self, context):
        self.write_debug_log(sys._getframe().f_code.co_name, context)

    def on_game_splatzone_we_lost(self, context):
        self.write_debug_log(sys._getframe().f_code.co_name, context)

    def on_game_splatzone_they_got(self, context):
        self.write_debug_log(sys._getframe().f_code.co_name, context)

    def on_game_splatzone_they_lost(self, context):
        self.write_debug_log(sys._getframe().f_code.co_name, context)

    # Ranked, Rainmaker battles

    def on_game_rainmaker_we_got(self, context):
        self.write_debug_log(sys._getframe().f_code.co_name, context)

    def on_game_rainmaker_we_lost(self, context):
        self.write_debug_log(sys._getframe().f_code.co_name, context)

    def on_game_rainmaker_they_got(self, context):
        self.write_debug_log(sys._getframe().f_code.co_name, context)

    def on_game_rainmaker_they_lost(self, context):
        self.write_debug_log(sys._getframe().f_code.co_name, context)

    # Ranked, Tower control battles

    def on_game_tower_we_got(self, context):
        self.write_debug_log(sys._getframe().f_code.co_name, context)

    def on_game_tower_we_lost(self, context):
        self.write_debug_log(sys._getframe().f_code.co_name, context)

    def on_game_tower_they_got(self, context):
        self.write_debug_log(sys._getframe().f_code.co_name, context)

    def on_game_tower_they_lost(self, context):
        self.write_debug_log(sys._getframe().f_code.co_name, context)

    # Counter / Object Tracking

    def on_game_paint_score_update(self, context):
        if 0:
            s = 'paint_score: %s' % context['game'].get('paint_score', 0)
            self.write_debug_log(sys._getframe().f_code.co_name, context,
                                 text=s)

    def on_game_objective_position_update(self, context):
        if 0:
            s = 'pos: %s' % context['game']['tower'].get('pos', 0)
            self.write_debug_log(sys._getframe().f_code.co_name, context,
                                 text=s)

    def on_game_splatzone_counter_update(self, context):
        if 0:
            s = 'my_team: %s(%s), counter_team: %s(%s)' % (
                context['game']['splatzone_my_team_counter']['value'],
                context['game']['splatzone_my_team_counter']['injury_value'],
                context['game']['splatzone_counter_team_counter']['value'],
                context['game']['splatzone_counter_team_counter'][
                    'injury_value'],
            )
            self.write_debug_log(sys._getframe().f_code.co_name, context,
                                 text=s)

    def on_game_special_gauge_update(self, context):
        if 0:
            s = 'special: %spct' % (context['game']['special_gauge'])
            self.write_debug_log(sys._getframe().f_code.co_name, context,
                                 text=s)

    # Result Scenes

    def on_result_judge(self, context):
        s = "judge: %s, knockout: %s" % (
            context['game'].get('judge', None), context['game'].get('knockout', None))

        self.write_debug_log(sys._getframe().f_code.co_name, context,
                             text=s)

    def on_game_individual_result(self, context):
        self.write_debug_log(sys._getframe().f_code.co_name, context)

    def on_result_udemae(self, context):
        result = context['scenes']['result_udemae']
        for field in result:
            if field.startswith('img_'):
                value = '(image)'

        self.write_debug_log(
            sys._getframe().f_code.co_name, context, text=result)

    def on_result_gears(self, context):
        self.write_debug_log(sys._getframe().f_code.co_name, context)

    def on_result_festa(self, context):
        game = context['game']
        s = 'festa change: %s -> %s title_changed %s' % (
            game.get('result_festa_exp_pre', None),
            game.get('result_festa_exp', None),
            game.get('result_festa_title_changed', None),
        )
        self.write_debug_log(sys._getframe().f_code.co_name, context, text=s)

    # Session end

    def on_game_session_end(self, context):
        s = "death_reasons = %s" % (context['game']['death_reasons'])
        self.write_debug_log(sys._getframe().f_code.co_name, context, text=s)

    def on_game_session_abort(self, context):
        self.write_debug_log(sys._getframe().f_code.co_name, context)

    def on_game_lost_sync(self, context):
        self.write_debug_log(sys._getframe().f_code.co_name, context)

    # Inkopolis

    def on_inkopolis_lottery_done(self, context):
        s = "\n  brand: %s\n  level: %d\n  new sub abilities: %s" % (
            context['game']['downie']['brand'],
            context['game']['downie']['level'],
            context['game']['downie']['sub_abilities']
        )
        self.write_debug_log(sys._getframe().f_code.co_name, context, text=s)

    # output: stat.ink
    def on_output_statink_submission_done(self, context, params={}):
        s = "url = %s" % params.get('url', None)
        self.write_debug_log(sys._getframe().f_code.co_name, context, text=s)

    def on_output_statink_submission_error(self, context, params={}):
        s = "url = %s" % params.get('url', None)
        self.write_debug_log(sys._getframe().f_code.co_name, context)

    def on_output_statink_submission_dryrun(self, context, params={}):
        self.write_debug_log(sys._getframe().f_code.co_name, context)

    def on_gear_select(self, context, params={}):
        self.write_debug_log(sys._getframe().f_code.co_name, context, text=params)


    # UI support

    def on_option_tab_create(self, notebook):
        pass

    # Constructor

    def __init__(self, dir='debug/', screenshot=False):
        self.dir = dir
        self.screenshot = screenshot
