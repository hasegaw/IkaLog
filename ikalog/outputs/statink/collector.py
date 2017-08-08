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
import math

from ikalog.constants import special_weapons
from ikalog.plugin import IkaLogPlugin
from ikalog.utils import *


class StatInkCollector(IkaLogPlugin):

    def on_validate_configuration(self, config):
        assert config['enabled'] in [True, False]
        return True

    def on_reset_configuration(self):
        config = self.config
        config['enabled'] = False

        config['api_key'] = ''
        config['endpoint_url'] = 'https://stat.ink/'
        config['dry_run'] = False
        config['debug_write_payload_to_file'] = False
        config['show_response'] = False

        config['track_inklings'] = True
        config['track_special_gauge'] = True
        config['track_special_weapon'] = True
        config['track_objective'] = True
        config['track_splatzone'] = True

        config['anon_all'] = False
        config['anon_others'] = False

    def on_set_configuration(self, config):
        self.config['enabled'] = config['enabled']
        self.config['api_key'] = config['api_key']

    def _get_offset_msec(self, context):
        if (context['engine'].get('msec') and
                context['game'].get('start_offset_msec')):
            return (context['engine']['msec'] -
                    context['game']['start_offset_msec'])
        return None

    def _add_event(self, context, event_data=None, time_delta=0.0):
        assert event_data is not None
        offset_msec = self._get_offset_msec(context)
        if (not 'at' in event_data) and offset_msec:
            # Use only the first decimal.
            event_data['at'] = int(offset_msec / 100) / 10 + time_delta
        else:
            IkaUtils.dprint('%s: Event %s not logged due to no timing information.' % (
                self, event_data['type']))
            return

        self.events.append(event_data)

    def _add_ranked_battle_event(self, context, event_sub_type=None):
        assert event_sub_type is not None
        self._add_event(context, {
            'type': 'ranked_battle_event',
            'value': event_sub_type,
        })

    def _open_game_session(self, context):
        self.events = []
        self.time_last_score_msec = None
        self.time_last_objective_msec = None
        self.time_last_special_gauge_msec = None
        self.last_dead_event = None

        self.img_scoreboard = None
        self.img_judge = None
        self.img_gears = None

        self._called_close_game_session = False

    def _close_game_session(self, context):
        if self._called_close_game_session:
            return
        self._called_close_game_session = True

        IkaUtils.dprint('%s: close_game_session called' % self)

        if (hasattr(self, 'close_game_session_handler')):
            self.close_game_session_handler(context)

    def on_reset_capture(self, context):
        self._open_game_session(context)

    def on_game_go_sign(self, context):
        self._open_game_session(context)

    def on_game_start(self, context):
        # ゴーサインをベースにカウントするが、ゴーサインを認識
        # できなかった場合の保険として on_game_start も拾っておく
        self._open_game_session(context)

    def on_game_finish(self, context):
        self._add_event(context, {'type': 'finish'})
        self.on_game_paint_score_update(context)

        # 戦績画面はこの後にくるはずなので今までにあるデータは捨てる
        self.img_scoreboard = None
        self.img_judge = None
        self.img_gears = None

        IkaUtils.dprint('%s: Discarded screenshots' % self)

    ##
    # on_result_detail_still Hook
    # @param self      The Object Pointer
    # @param context   IkaLog context
    #
    def on_result_detail_still(self, context):
        self.img_scoreboard = context['game']['image_scoreboard']
        IkaUtils.dprint('%s: Gathered img_result (%s)' %
                        (self, self.img_scoreboard.shape))

    def on_result_judge(self, context):
        self.img_judge = context['game'].get('image_judge', None)
        IkaUtils.dprint('%s: Gathered img_judge(%s)' %
                        (self, self.img_judge.shape))

    def on_result_gears_still(self, context):
        self.img_gears = context['game']['image_gears']
        IkaUtils.dprint('%s: Gathered img_gears (%s)' %
                        (self, self.img_gears.shape))

    def on_game_session_end(self, context):
        self._close_game_session(context)

    def on_game_session_abort(self, context):
        self._close_game_session(context)

    def on_game_killed(self, context, params):
        self._add_event(context, {'type': 'killed'})

    def on_game_dead(self, context):
        self.last_dead_event = {'type': 'dead'}
        self._add_event(context, self.last_dead_event, time_delta=-2.0)

    def on_game_death_reason_identified(self, context):
        # 死因が特定されたら最後の死亡イベントに追加する
        if self.last_dead_event is not None:
            reason = context['game']['last_death_reason']
            self.last_dead_event['reason'] = reason
            self.last_dead_event = None

    def on_game_low_ink(self, context):
        self._add_event(context, {'type': 'low_ink'})

    def on_game_map_open(self, context):
        self._last_map_open_event = {'type': 'map_view'}
        self._last_map_open_msec = context['engine']['msec']

        self._add_event(context, self._last_map_open_event)

    def on_game_map_close(self, context):
        if self._last_map_open_event is not None:
            duration = context['engine']['msec'] - self._last_map_open_msec
            duration_sec = math.floor(duration / 100) / 10

            self._last_map_open_event['seconds'] = duration_sec
            self._last_map_open_event = None

    def on_game_inkling_state_update(self, context):
        if not self.config['track_inklings']:
            return

        if self._get_offset_msec(context):
            self._add_event(context, {
                'type': 'alive_inklings',
                'my_team': context['game']['inkling_state'][0],
                'his_team': context['game']['inkling_state'][1],
            })

    def on_game_game_status_update(self, context, params):
        self._add_event(context, {
            'type': 'game_status',
            'game_status': params['game_status'],
        })

    def on_game_paint_score_update(self, context):
        score = context['game'].get('paint_score', 0)
        event_msec = self._get_offset_msec(context)
        if (score > 0) and event_msec:
            # 前回のスコアイベントから 200ms 経っていない場合は処理しない
            if (self.time_last_score_msec is None) or (event_msec - self.time_last_score_msec >= 200):
                self._add_event(context, {
                    'type': 'point',
                    'point': score,
                })
                self.time_last_score_msec = event_msec

    def on_game_special_gauge_update(self, context):
        if not self.config['track_special_gauge']:
            return

        score = context['game'].get('special_gauge', 0)
        event_msec = self._get_offset_msec(context)
        if (score > 0) and event_msec:
            # 前回のスコアイベントから 200ms 経っていない場合は処理しない
            if (self.time_last_special_gauge_msec is None) or (event_msec - self.time_last_special_gauge_msec >= 200):
                self._add_event(context, {
                    'type': 'special%',
                    'point': score,
                })
                self.time_last_special_gauge_msec = event_msec

    def on_game_special_gauge_charged(self, context):
        if not self.config['track_special_gauge']:
            return

        event_msec = self._get_offset_msec(context)
        if event_msec:
            self._add_event(context, {
                'type': 'special_charged',
            })

    def on_game_special_weapon(self, context):
        if not self.config['track_special_weapon']:
            return

        special_weapon = context['game'].get('special_weapon', None)
        if not (special_weapon in special_weapons.keys()):
            IkaUtils.dprint('%s: special_weapon %s is invalid.' %
                            (self, special_weapon))
            return

        event_msec = self._get_offset_msec(context)
        if event_msec:
            self._add_event(context, {
                'type': 'special_weapon',
                'special_weapon': special_weapon,
                'me': context['game'].get('special_weapon_is_mine', False),
            })

    def on_game_objective_position_update(self, context):
        if not self.config['track_objective']:
            return

        event_msec = self._get_offset_msec(context)

        if (self.time_last_objective_msec is None) or (event_msec - self.time_last_objective_msec >= 200):
            self._add_event(context, {
                'type': 'objective',
                'position': context['game']['tower'].get('pos', 0),
            })
            self.time_last_objective_msec = event_msec

    def on_game_splatzone_counter_update(self, context):
        if not self.config['track_splatzone']:
            return

        event_msec = self._get_offset_msec(context)
        self._add_event(context, {
            'type': 'splatzone',
            'my_team_count': context['game']['splatzone_my_team_counter']['value'],
            'my_team_injury_count': None,
            'his_team_count': context['game']['splatzone_counter_team_counter']['value'],
            'his_team_injury_count': None,
        })
        self.time_last_score_msec = event_msec

    def on_game_splatzone_we_got(self, context):
        self._add_ranked_battle_event(context, 'we_got')

    def on_game_splatzone_we_lost(self, context):
        self._add_ranked_battle_event(context, 'we_lost')

    def on_game_splatzone_they_got(self, context):
        self._add_ranked_battle_event(context, 'they_got')

    def on_game_splatzone_they_lost(self, context):
        self._add_ranked_battle_event(context, 'they_lost')

    def on_game_rainmaker_we_got(self, context):
        self._add_ranked_battle_event(context, 'we_got')

    def on_game_rainmaker_we_lost(self, context):
        self._add_ranked_battle_event(context, 'we_lost')

    def on_game_rainmaker_they_got(self, context):
        self._add_ranked_battle_event(context, 'they_got')

    def on_game_rainmaker_they_lost(self, context):
        self._add_ranked_battle_event(context, 'they_lost')

    def on_game_towercontrol_we_took(self, context):
        self._add_ranked_battle_event(context, 'we_got')

    def on_game_towercontrol_we_lost(self, context):
        self._add_ranked_battle_event(context, 'we_lost')

    def on_game_towercontrol_they_took(self, context):
        self._add_ranked_battle_event(context, 'they_got')

    def on_game_towercontrol_they_lost(self, context):
        self._add_ranked_battle_event(context, 'they_lost')

    def on_game_ranked_we_lead(self, context):
        self._add_ranked_battle_event(context, 'we_lead')

    def on_game_ranked_they_lead(self, context):
        self._add_ranked_battle_event(context, 'they_lead')

    def __init__(self):
        super(StatInkCollector, self).__init__()

        self._last_map_open_event = None

        self._open_game_session(None)

        # If true, it means the payload is not posted or saved.
        self._called_close_game_session = False
