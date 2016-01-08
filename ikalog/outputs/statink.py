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
import json
import os
import pprint
import threading
import time

import cv2
import urllib3
import umsgpack

from ikalog.constants import fes_rank_titles, stages, weapons
from ikalog.version import IKALOG_VERSION
from ikalog.utils import *

t = gettext.translation('statink', 'locale', fallback=True)
_ = t.gettext

# Needed in GUI mode
try:
    import wx
except:
    pass

# @package ikalog.outputs.statink

# IkaLog Output Plugin for Stat.ink


class StatInk(object):

    def apply_ui(self):
        self.enabled = self.checkEnable.GetValue()
        self.show_response_enabled = self.checkShowResponseEnable.GetValue()
        self.track_objective_enabled = self.checkTrackObjectiveEnable.GetValue()
        self.track_splatzone_enabled = self.checkTrackSplatzoneEnable.GetValue()
        self.api_key = self.editApiKey.GetValue()

    def refresh_ui(self):
        self.checkEnable.SetValue(self.enabled)
        self.checkShowResponseEnable.SetValue(self.show_response_enabled)
        self.checkTrackObjectiveEnable.SetValue(self.track_objective_enabled)
        self.checkTrackSplatzoneEnable.SetValue(self.track_splatzone_enabled)

        if not self.api_key is None:
            self.editApiKey.SetValue(self.api_key)
        else:
            self.editApiKey.SetValue('')

    def on_config_reset(self, context=None):
        self.enabled = False
        self.show_response_enabled = False
        self.track_objective_enabled = False
        self.track_splatzone_enabled = False
        self.api_key = None

    def on_config_load_from_context(self, context):
        self.on_config_reset(context)
        try:
            conf = context['config']['stat.ink']
        except:
            conf = {}

        self.enabled = conf.get('Enable', False)
        self.show_response_enabled = conf.get('ShowResponse', False)
        self.track_objective_enabled = conf.get('TrackObjective', False)
        self.track_splatzone_enabled = conf.get('TrackSplatzone', False)
        self.api_key = conf.get('APIKEY', '')

        self.refresh_ui()
        return True

    def on_config_save_to_context(self, context):
        context['config']['stat.ink'] = {
            'Enable': self.enabled,
            'ShowResponse': self.show_response_enabled,
            'TrackObjective': self.track_objective_enabled,
            'TrackSplatzone': self.track_splatzone_enabled,
            'APIKEY': self.api_key,
        }

    def on_config_apply(self, context):
        self.apply_ui()

    def on_option_tab_create(self, notebook):
        self.panel = wx.Panel(notebook, wx.ID_ANY)
        self.page = notebook.InsertPage(0, self.panel, _('stat.ink'))
        self.layout = wx.BoxSizer(wx.VERTICAL)
        self.panel.SetSizer(self.layout)
        self.checkEnable = wx.CheckBox(
            self.panel, wx.ID_ANY, _('Post game results to stat.ink'))
        self.checkTrackObjectiveEnable = wx.CheckBox(
            self.panel, wx.ID_ANY, _('Include position data of tracked objectives (experimental)'))
        self.checkTrackSplatzoneEnable = wx.CheckBox(
            self.panel, wx.ID_ANY, _('Include Splat Zone counters (experimental'))
        self.checkShowResponseEnable = wx.CheckBox(
            self.panel, wx.ID_ANY, _('Show stat.ink response in console'))
        self.editApiKey = wx.TextCtrl(self.panel, wx.ID_ANY, u'hoge')

        self.layout.Add(self.checkEnable)
        self.layout.Add(self.checkShowResponseEnable)
        self.layout.Add(self.checkTrackObjectiveEnable)
        self.layout.Add(self.checkTrackSplatzoneEnable)
        self.layout.Add(wx.StaticText(
            self.panel, wx.ID_ANY, _('API Key')))
        self.layout.Add(self.editApiKey, flag=wx.EXPAND)

        self.panel.SetSizer(self.layout)

    def encode_stage_name(self, context):
        stage_id = IkaUtils.map2id(context['game']['map'], unknown=None)
        return stage_id

    def encode_rule_name(self, context):
        rule_id = IkaUtils.rule2id(context['game']['rule'], unknown=None)
        return rule_id

    def encode_weapon_name(self, weapon):
        # FIXME: 現状返ってくる key が日本語表記なので id に変換
        weapon_id = None
        for k in weapons:
            if weapons[k]['ja'] == weapon:
                weapon_id = k

        if (weapon_id is None) and (weapons.get(weapon, None) is not None):
            weapon_id = weapon

        if weapon_id is None:
            IkaUtils.dprint(
                '%s: Failed convert weapon name %s to stas.ink value' % (self, weapon))
        return weapon_id

    def encode_image(self, img):
        result, img_png = cv2.imencode('.png', img)

        if not result:
            IkaUtils.dprint('%s: Failed to encode the image (%s)' %
                            (self, img.shape))
            return None

        s = img_png.tostring()

        IkaUtils.dprint('%s: Encoded screenshot (%dx%d %d bytes)' %
                        (self, img.shape[1], img.shape[0], len(s)))

        return s

    def _set_values(self, fields, dest, src):
        for field in fields:

            f_type = field[0]
            f_statink = field[1]
            f_ikalog = field[2]

            if (f_ikalog in src) and (src[f_ikalog] is not None):
                if f_type == 'int':
                    try:
                        dest[f_statink] = int(src[f_ikalog])
                    except:  # ValueError
                        IkaUtils.dprint('%s: field %s failed: src[%s] == %s' % (
                            self, f_statink, f_ikalog, src[f_ikalog]))
                        pass
                elif f_type == 'str':
                    dest[f_statink] = str(src[f_ikalog])
                elif f_type == 'str_lower':
                    dest[f_statink] = str(src[f_ikalog]).lower()

    def _add_event(self, context, event_data=None):
        assert event_data is not None
        if (not 'at'in event_data) and (self.time_start_at_msec is not None):
            offset_msec = context['engine']['msec'] - self.time_start_at_msec
            event_data['at'] = int(offset_msec / 100) / 10
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

    def composite_payload(self, context):
        payload = {}

        # Lobby

        lobby_type = context['lobby'].get('type', None)
        if lobby_type == 'public':
            payload['lobby'] = 'standard'

        elif lobby_type == 'private':
            payload['lobby'] = 'private'

        elif context['game']['is_fes'] or (lobby_type == 'festa'):
            payload['lobby'] = 'fest'

        elif lobby_type == 'tag':
            num_members = context['lobby'].get('team_members', None)
            if num_members in [2, 3, 4]:
                payload['lobby'] = 'squad_%d' % num_members
            else:
                IkaUtils.dprint('%s: invalid lobby key squad_%s' %
                                (self, num_members))

        else:
            IkaUtils.dprint('%s: No lobby information.' % self)

        # GameStart

        stage = self.encode_stage_name(context)
        if stage:
            payload['map'] = stage

        rule = self.encode_rule_name(context)
        if rule:
            payload['rule'] = rule

        if self.time_start_at and self.time_end_at:
            payload['start_at'] = int(self.time_start_at)
            payload['end_at'] = int(self.time_end_at)

        # In-game logs

        if len(context['game']['death_reasons'].keys()) > 0:
            payload['death_reasons'] = context['game']['death_reasons'].copy()

        if len(self.events) > 0:
            payload['events'] = list(self.events)

        # ResultJudge

        if payload.get('rule', None) in ['nawabari']:
            scores = context['game'].get('nawabari_scores_pct', None)
            print('nawabari scores = %s' % scores)
            if scores is not None:
                payload['my_team_final_percent'] = scores[0]
                payload['his_team_final_percent'] = scores[1]

        if payload.get('rule', None) in ['area', 'yagura', 'hoko']:
            scores = context['game'].get('ranked_scores', None)
            print('ranked scores = %s' % scores)
            if scores is not None:
                payload['my_team_count'] = scores[0]
                payload['his_team_count'] = scores[1]

        scores = context['game'].get('earned_scores', None)
        if 0:  # scores is not None:
            payload['my_team_final_point'] = scores[0]
            payload['his_team_final_point'] = scores[1]

        # ResultDetail

        me = IkaUtils.getMyEntryFromContext(context)

        payload['result'] = IkaUtils.getWinLoseText(
            context['game']['won'],
            win_text='win',
            lose_text='lose',
            unknown_text=None
        )

        if 'weapon' in me:
            weapon = self.encode_weapon_name(me['weapon'])
            if weapon:
                payload['weapon'] = weapon

        if context['game']['is_fes']:
            payload['gender'] = me['gender_en']
            payload['fest_title'] = str(me['prefix_en']).lower()

        self._set_values(
            [  # 'type', 'stat.ink Field', 'IkaLog Field'
                ['int', 'rank_in_team', 'rank_in_team'],
                ['int', 'kill', 'kills'],
                ['int', 'death', 'deaths'],
                ['int', 'level', 'rank'],
                ['int', 'my_point', 'score'],
            ], payload, me)

        players = []
        for e in context['game']['players']:
            player = {}
            player['team'] = 'my' if (e['team'] == me['team']) else 'his'
            player['is_me'] = 'yes' if e['me'] else 'no'
            self._set_values(
                [  # 'type', 'stat.ink Field', 'IkaLog Field'
                    ['int', 'rank_in_team', 'rank_in_team'],
                    ['int', 'kill', 'kills'],
                    ['int', 'death', 'deaths'],
                    ['int', 'level', 'rank'],
                    ['int', 'point', 'score'],
                ], player, e)

            if 'weapon' in e:
                weapon = self.encode_weapon_name(e['weapon'])
                if weapon:
                    player['weapon'] = weapon

            if payload.get('rule', 'nawabari') != 'nawabari':
                if 'udemae_pre' in e:
                    player['rank'] = str(e['udemae_pre']).lower()

            players.append(player)

        payload['players'] = players

        # ResultGears

        try:
            gears_list = []
            for e in context['scenes']['result_gears']['gears']:
                primary_ability = e.get('main', None)
                secondary_abilities = [
                    e.get('sub1', None),
                    e.get('sub2', None),
                    e.get('sub3', None),
                ]

                gear = {'secondary_abilities': []}
                if primary_ability is not None:
                    gear['primary_ability'] = primary_ability

                for ability in secondary_abilities:
                    if (ability is None) or (ability == 'empty'):
                        continue
                    gear['secondary_abilities'].append(ability)

                gears_list.append(gear)

            payload['gears'] = {
                'headgear': gears_list[0],
                'clothing': gears_list[1],
                'shoes': gears_list[2],
            }
        except:
            IkaUtils.dprint(
                '%s: Failed in ResultGears payload. Fix me...' % self)
            IkaUtils.dprint(traceback.format_exc())

        # ResultUdemae

        if payload.get('rule', 'nawabari') != 'nawabari':
            self._set_values(
                [  # 'type', 'stat.ink Field', 'IkaLog Field'
                    ['str_lower', 'rank', 'result_udemae_str_pre'],
                    ['int', 'rank_exp', 'result_udemae_exp_pre'],
                    ['str_lower', 'rank_after', 'result_udemae_str'],
                    ['int', 'rank_exp_after', 'result_udemae_exp'],
                ], payload, context['game'])

        knockout = context['game'].get('knockout', None)
        if (payload.get('rule', 'nawabari') != 'nawabari') and (knockout is not None):
            payload['knock_out'] = {True: 'yes', False: 'no'}[knockout]

        # ResultGears

        if 'result_gears' in context['scenes']:
            self._set_values(
                [  # 'type', 'stat.ink Field', 'IkaLog Field'
                    ['int', 'cash_after', 'cash'],
                ], payload, context['scenes']['result_gears'])

        # ResultFesta
        if payload.get('lobby', None) == 'fest':
            self._set_values(
                [  # 'type', 'stat.ink Field', 'IkaLog Field'
                    ['int', 'fest_exp', 'result_festa_exp_pre'],
                    ['int', 'fest_exp_after', 'result_festa_exp'],
                ], payload, context['game'])

            if payload.get('fest_title', None) is not None:
                current_title = payload['fest_title']
                if context['game'].get('result_festa_title_changed', False):
                    try:
                        index = fes_rank_titles.index(current_title)
                        current_title = fes_rank_titles[index + 1]
                    except IndexError:
                        IkaUtils.dprint(
                            '%s: IndexError at fes_rank_titles' % self)

                payload['fest_title_after'] = current_title.lower()

        # Team colors
        if ('my_team_color' in context['game']):
            payload['my_team_color'] = {
                'hue': context['game']['my_team_color']['hsv'][0] * 2,
                'rgb': context['game']['my_team_color']['rgb'],
            }
            payload['his_team_color'] = {
                'hue': context['game']['counter_team_color']['hsv'][0] * 2,
                'rgb': context['game']['counter_team_color']['rgb'],
            }

        # Screenshots

        if self.img_result_detail is not None:
            payload['image_result'] = self.encode_image(self.img_result_detail)
        else:
            IkaUtils.dprint('%s: img_result_detail is empty.' % self)

        if self.img_judge is not None:
            payload['image_judge'] = self.encode_image(self.img_judge)
        else:
            IkaUtils.dprint('%s: img_judge is empty.' % self)

        # Agent Information

        payload['agent'] = 'IkaLog'
        payload['agent_version'] = IKALOG_VERSION

        for field in payload.keys():
            if payload[field] is None:
                IkaUtils.dprint('%s: [FIXME] payload has blank entry %s:%s' % (
                    self, field, payload[field]))

        return payload

    def write_response_to_file(self, r_header, r_body, basename=None):
        if basename is None:
            t = datetime.now().strftime("%Y%m%d_%H%M")
            basename = os.path.join('/tmp', 'statink_%s' % t)

        try:
            f = open(basename + '.r_header', 'w')
            f.write(r_header)
            f.close()
        except:
            IkaUtils.dprint('%s: Failed to write file' % self)
            IkaUtils.dprint(traceback.format_exc())

        try:
            f = open(basename + '.r_body', 'w')
            f.write(r_body)
            f.close()
        except:
            IkaUtils.dprint('%s: Failed to write file' % self)
            IkaUtils.dprint(traceback.format_exc())

    def write_payload_to_file(self, payload, basename=None):
        if basename is None:
            t = datetime.now().strftime("%Y%m%d_%H%M")
            basename = os.path.join('/tmp', 'statink_%s' % t)

        try:
            f = open(basename + '.msgpack', 'w')
            f.write(''.join(map(chr, umsgpack.packb(payload))))
            f.close()
        except:
            IkaUtils.dprint('%s: Failed to write msgpack file' % self)
            IkaUtils.dprint(traceback.format_exc())

    def _post_payload_worker(self, payload):
        if self.dry_run == 'server':
            payload['test'] = 'dry_run'

        mp_payload_bytes = umsgpack.packb(payload)
        mp_payload = ''.join(map(chr, mp_payload_bytes))

        url_statink_v1_battle = 'https://stat.ink/api/v1/battle'

        http_headers = {
            'Content-Type': 'application/x-msgpack',
        }

        IkaUtils.dprint('%s: POST %s' % (self, url_statink_v1_battle))

        pool = urllib3.PoolManager(
            cert_reqs = 'CERT_REQUIRED', # Force certificate check
            ca_certs = Certifi.where(),  # Path to the Certifi bundle.
        )

        try:
            req = pool.urlopen('POST', url_statink_v1_battle,
                               headers=http_headers,
                               body=mp_payload,
                               )
        except urllib3.exceptions.SSLError as e:
            # Handle incorrect certificate error.
            IkaUtils.dprint('%s: SSLError, value: %s' % (self, e.value))

        IkaUtils.dprint('%s: POST Done.' % self)

        statink_reponse = json.loads(req.data.decode('utf-8'))
        error = 'error' in statink_reponse
        if error:
            IkaUtils.dprint('%s: API Error occured')

        if self.show_response_enabled or error:
            IkaUtils.dprint('%s: == Response begin ==' % self)
            print(req.data.decode('utf-8'))
            IkaUtils.dprint('%s: == Response end ===' % self)

    def post_payload(self, payload, api_key=None):
        if self.dry_run == True:
            IkaUtils.dprint(
                '%s: Dry-run mode, skipping POST to stat.ink.' % self)

        if api_key is None:
            api_key = self.api_key

        if api_key is None:
            raise('No API key specified')

        # Payload data will be modified, so we copy it.
        # It is not deep copy, so only dict object is
        # duplicated.
        payload = payload.copy()
        payload['apikey'] = api_key

        thread = threading.Thread(
            target=self._post_payload_worker, args=(payload,))
        thread.start()

    def print_payload(self, payload):
        payload = payload.copy()

        if 'image_result' in payload:
            payload['image_result'] = '(PNG Data)'
        if 'image_judge' in payload:
            payload['image_judge'] = '(PNG Data)'
        if 'events' in payload:
            payload['events'] = '(Events)'

        pprint.pprint(payload)

    def on_game_go_sign(self, context):
        self.time_start_at = int(time.time())
        self.time_end_at = None
        self.events = []
        self.time_last_score_msec = None
        self.time_last_objective_msec = None
        self.last_dead_event = None

        # check if context['engine']['msec'] exists
        # to allow unit test.
        if 'msec' in context['engine']:
            self.time_start_at_msec = context['engine']['msec']

    def on_game_start(self, context):
        # ゴーサインをベースにカウントするが、ゴーサインを認識
        # できなかった場合の保険として on_game_start も拾っておく
        self.on_game_go_sign(context)

    def on_game_finish(self, context):
        self.time_end_at = int(time.time())
        if ('msec' in context['engine']) and (self.time_start_at_msec is not None):
            duration_msec = context['engine']['msec'] - self.time_start_at_msec

            if duration_msec >= 0.0:
                self.time_start_at = int(
                    self.time_end_at - int(duration_msec / 1000))

        self.on_game_paint_score_update(context)

        # 戦績画面はこの後にくるはずなので今までにあるデータは捨てる
        self.img_result_detail = None
        self.img_judge = None

        IkaUtils.dprint('%s: Discarded screenshots' % self)

    ##
    # on_result_detail_still Hook
    # @param self      The Object Pointer
    # @param context   IkaLog context
    #
    def on_result_detail_still(self, context):
        self.img_result_detail = context['engine']['frame']
        IkaUtils.dprint('%s: Gathered img_result (%s)' %
                        (self, self.img_result_detail.shape))

    def on_result_judge(self, context):
        self.img_judge = context['game'].get('image_judge', None)
        IkaUtils.dprint('%s: Gathered img_judge(%s)' %
                        (self, self.img_judge.shape))

    def on_game_session_end(self, context):
        IkaUtils.dprint('%s (enabled = %s)' % (self, self.enabled))

        if (not self.enabled) and (not self.dry_run):
            return False

        payload = self.composite_payload(context)

        self.print_payload(payload)

        if self.debug_writePayloadToFile:
            self.write_payload_to_file(payload)

        self.post_payload(payload)

    def on_game_killed(self, context):
        self._add_event(context, {'type': 'killed'})

    def on_game_dead(self, context):
        self.last_dead_event = {'type': 'dead'}
        self._add_event(context, self.last_dead_event)

    def on_game_death_reason_identified(self, context):
        # 死因が特定されたら最後の死亡イベントに追加する
        if self.last_dead_event is not None:
            reason = context['game']['last_death_reason']
            self.last_dead_event['reason'] = reason
            self.last_dead_event = None

    def on_game_paint_score_update(self, context):
        score = context['game'].get('paint_score', 0)
        if (score > 0 and 'msec' in context['engine']) and (self.time_start_at_msec is not None):
            event_msec = context['engine']['msec'] - self.time_start_at_msec
            # 前回のスコアイベントから 200ms 経っていない場合は処理しない
            if (self.time_last_score_msec is None) or (event_msec - self.time_last_score_msec >= 200):
                self._add_event(context, {
                    'type': 'point',
                    'point': score,
                })
                self.time_last_score_msec = event_msec

    def on_game_objective_position_update(self, context):
        if not self.track_objective_enabled:
            return

        event_msec = context['engine']['msec'] - self.time_start_at_msec

        if (self.time_last_objective_msec is None) or (event_msec - self.time_last_objective_msec >= 200):
            self._add_event(context, {
                'type': 'objective',
                'position': context['game']['tower'].get('pos', 0),
            })
            self.time_last_objective_msec = event_msec

    def on_game_splatzone_counter_update(self, context):
        if not self.track_splatzone_enabled:
            return

        event_msec = context['engine']['msec'] - self.time_start_at_msec
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

    def __init__(self, api_key=None, track_objective=False, track_splatzone=False, debug=False, dry_run=False):
        self.enabled = not (api_key is None)
        self.api_key = api_key
        self.dry_run = dry_run

        self.time_start_at = None
        self.time_end_at = None
        self.time_start_at_msec = None

        self.events = []
        self.time_last_score_msec = None
        self.time_last_objective_msec = None
        self.last_dead_event = None

        self.img_result_detail = None
        self.img_judge = None

        self.debug_writePayloadToFile = False
        self.show_response_enabled = debug
        self.track_objective_enabled = track_objective
        self.track_splatzone_enabled = track_splatzone

if __name__ == "__main__":
    # main として呼ばれた場合
    #
    # 第一引数で指定された戦績画面スクリーンショットを、
    # ハコフグ倉庫・ガチエリアということにして Post する
    #
    # APIキーを環境変数 IKALOG_STATINK_APIKEY に設定して
    # おくこと

    from ikalog.scenes.result_detail import *

    obj = StatInk(
        api_key=os.environ['IKALOG_STATINK_APIKEY'],
        dry_run=False,
        debug=True,
    )

    # 最低限の context
    file = sys.argv[1]
    context = {
        'engine': {
            'frame': cv2.imread(file),
        },
        'game': {
            'map': {'name': 'ハコフグ倉庫', },
            'rule': {'name': 'ガチエリア'},
            'death_reasons': {},
        },
        'scenes': {
        },
        'lobby': {
        },
    }

    # 各プレイヤーの状況を分析
    ResultDetail().analyze(context)

    # stat.ink へのトリガ
    obj.on_game_session_end(context)
