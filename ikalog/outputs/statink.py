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

import time
import os
import pprint

import urllib3
import umsgpack

from ikalog.constants import fes_rank_titles
from ikalog.version import IKALOG_VERSION
from ikalog.utils import *


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
        self.api_key = self.editApiKey.GetValue()

    def refresh_ui(self):
        self.checkEnable.SetValue(self.enabled)
        self.checkShowResponseEnable.SetValue(self.show_response_enabled)

        if not self.api_key is None:
            self.editApiKey.SetValue(self.api_key)
        else:
            self.editApiKey.SetValue('')

    def on_config_reset(self, context=None):
        self.enabled = False
        self.show_response_enabled = False
        self.api_key = None

    def on_config_load_from_context(self, context):
        self.on_config_reset(context)
        try:
            conf = context['config']['stat.ink']
        except:
            conf = {}

        if 'Enable' in conf:
            self.enabled = conf['Enable']

        if 'ShowResponse' in conf:
            self.show_response_enabled = conf['ShowResponse']

        if 'APIKEY' in conf:
            self.api_key = conf['APIKEY']

        self.refresh_ui()
        return True

    def on_config_save_to_context(self, context):
        context['config']['stat.ink'] = {
            'Enable': self.enabled,
            'ShowResponse': self.show_response_enabled,
            'APIKEY': self.api_key,
        }

    def on_config_apply(self, context):
        self.apply_ui()

    def on_option_tab_create(self, notebook):
        self.panel = wx.Panel(notebook, wx.ID_ANY)
        self.page = notebook.InsertPage(0, self.panel, 'stat.ink')
        self.layout = wx.BoxSizer(wx.VERTICAL)
        self.panel.SetSizer(self.layout)
        self.checkEnable = wx.CheckBox(
            self.panel, wx.ID_ANY, 'stat.ink へのスコアを送信する')
        self.checkShowResponseEnable = wx.CheckBox(
            self.panel, wx.ID_ANY, 'stat.ink からの応答をコンソールに出力する')
        self.editApiKey = wx.TextCtrl(self.panel, wx.ID_ANY, u'hoge')

        self.layout.Add(self.checkEnable)
        self.layout.Add(self.checkShowResponseEnable)
        self.layout.Add(wx.StaticText(
            self.panel, wx.ID_ANY, u'APIキー'))
        self.layout.Add(self.editApiKey, flag=wx.EXPAND)

        self.panel.SetSizer(self.layout)

    def encode_stage_name(self, context):
        try:
            stage = IkaUtils.map2text(context['game']['map'])
            return {
                'アロワナモール': 'arowana',
                'Bバスパーク': 'bbass',
                'デカライン高架下': 'dekaline',
                'ハコフグ倉庫': 'hakofugu',
                'ヒラメが丘団地': 'hirame',
                'ホッケふ頭': 'hokke',
                'キンメダイ美術館': 'kinmedai',
                'マサバ海峡大橋': 'masaba',
                'モンガラキャンプ場': 'mongara',
                'モズク農園': 'mozuku',
                'ネギトロ炭鉱': 'negitoro',
                'シオノメ油田': 'shionome',
                'タチウオパーキング': 'tachiuo'
            }[stage]
        except:
            IkaUtils.dprint(
                '%s: Failed convert staage name %s to stat.ink value' % (self, stage))
            return None

    def encode_rule_name(self, context):
        try:
            rule = IkaUtils.rule2text(context['game']['rule'])
            return {
                'ナワバリバトル': 'nawabari',
                'ガチエリア': 'area',
                'ガチヤグラ': 'yagura',
                'ガチホコバトル': 'hoko',
            }[rule]
        except:
            IkaUtils.dprint(
                '%s: Failed convert rule name %s to stat.ink value' % (self, rule))
            return None

    def encode_weapon_name(self, weapon):
        try:
            return {
                'ガロン52': '52gal',
                'ガロンデコ52': '52gal_deco',
                'ガロン96': '96gal',
                'ガロンデコ96': '96gal_deco',
                'ボールドマーカー': 'bold',
                'ボールドマーカーネオ': 'bold_neo',
                'デュアルスイーパー': 'dualsweeper',
                'デュアルスイーパーカスタム': 'dualsweeper_custom',
                'H3リールガン': 'h3reelgun',
                'H3リールガンD': 'h3reelgun_d',
                'ハイドラント': 'hydra',
                'ヒーローシューターレプリカ': 'heroshooter_replica',
                'ホットブラスター': 'hotblaster',
                'ホットブラスターカスタム': 'hotblaster_custom',
                'ジェットスイーパー': 'jetsweeper',
                'ジェットスイーパーカスタム': 'jetsweeper_custom',
                'L3リールガン': 'l3reelgun',
                'L3リールガンD': 'l3reelgun_d',
                'ロングブラスター': 'longblaster',
                'ロングブラスターカスタム': 'longblaster_custom',
                'もみじシューター': 'momiji',
                'ノヴァブラスター': 'nova',
                'ノヴァブラスターネオ': 'nova_neo',
                'N-ZAP85': 'nzap85',
                'N-ZAP89': 'nzap89',
                'オクタシューターレプリカ': 'octoshooter_replica',
                'プライムシューター': 'prime',
                'プライムシューターコラボ': 'prime_collabo',
                'プロモデラーMG': 'promodeler_mg',
                'プロモデラーRG': 'promodeler_rg',
                'ラピッドブラスター': 'rapid',
                'ラピッドブラスターデコ': 'rapid_deco',
                'Rブラスターエリート': 'rapid_elite',
                'シャープマーカー': 'sharp',
                'シャープマーカーネオ': 'sharp_neo',
                'スプラシューター': 'sshooter',
                'スプラシューターコラボ': 'sshooter_collabo',
                'わかばシューター': 'wakaba',

                'カーボンローラー': 'carbon',
                'カーボンローラーデコ': 'carbon_deco',
                'ダイナモローラー': 'dynamo',
                'ダイナモローラーテスラ': 'dynamo_tesla',
                'ヒーローローラーレプリカ': 'heroroller_replica',
                'ホクサイ': 'hokusai',
                'パブロ': 'pablo',
                'パブロ・ヒュー': 'pablo_hue',
                'スプラローラー': 'splatroller',
                'スプラローラーコラボ': 'splatroller_collabo',

                '14式竹筒銃・甲': 'bamboo14mk1',
                '14式竹筒銃・乙': 'bamboo14mk2',
                'ヒーローチャージャーレプリカ': 'herocharger_replica',
                'リッター3K': 'liter3k',
                'リッター3Kカスタム': 'liter3k_custom',
                '3Kスコープ': 'liter3k_scope',
                '3Kスコープカスタム': 'liter3k_scope_custom',
                'スプラチャージャー': 'splatcharger',
                'スプラチャージャーワカメ': 'splatcharger_wakame',
                'スプラスコープ': 'splatscope',
                'スプラスコープワカメ': 'splatscope_wakame',
                'スクイックリンα': 'squiclean_a',
                'スクイックリンβ': 'squiclean_b',

                'バケットスロッシャー': 'bucketslosher',
                'バケットスロッシャーデコ': 'bucketslosher_deco',
                'ヒッセン': 'hissen',
                'スクリュースロッシャー': 'screwslosher'

                'バレルスピナー': 'barrelspinner',
                'バレルスピナーデコ': 'barrelspinner_deco',
                'スプラスピナー': 'splatspinner',
            }[weapon]
        except:
            IkaUtils.dprint(
                '%s: Failed convert weapon name %s to stas.ink value' % (self, weapon))
            return None

    def encode_image(self, img):
        if IkaUtils.isWindows():
            temp_file = os.path.join(
                os.environ['TMP'], '_image_for_statink.png')
        else:
            temp_file = '_image_for_statink.png'

        IkaUtils.dprint('%s: Using temporary file %s' % (self, temp_file))

        try:
            if os.path.exists(temp_file):
                os.remove(temp_file)
        except:
            IkaUtils.dprint(
                '%s: Failed to remove existing temporary file %s' % (self, temp_file))
            IkaUtils.dprint(traceback.format_exc())

        try:
            # ToDo: statink accepts only 16x9
            IkaUtils.writeScreenshot(temp_file, img)
            f = open(temp_file, 'rb')
            s = f.read()
            try:
                f.close()
                os.remove(temp_file)
            except:
                pass
        except:
            IkaUtils.dprint('%s: Failed to attach image_result' % self)
            return None

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
        if payload.get('lobby',None) == 'fest':
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
                        IkaUtils.dprint('%s: IndexError at fes_rank_titles' % self)

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

    def post_payload(self, payload, api_key=None):
        if self.dry_run:
            IkaUtils.dprint(
                '%s: Dry-run mode, skipping POST to stat.ink.' % self)
            return

        url_statink_v1_battle = 'https://stat.ink/api/v1/battle'

        if api_key is None:
            api_key = self.api_key

        if api_key is None:
            raise('No API key specified')

        http_headers = {
            'Content-Type': 'application/x-msgpack',
        }

        # Payload data will be modified, so we copy it.
        # It is not deep copy, so only dict object is
        # duplicated.
        payload = payload.copy()
        payload['apikey'] = api_key
        mp_payload_bytes = umsgpack.packb(payload)
        mp_payload = ''.join(map(chr, mp_payload_bytes))

        pool = urllib3.PoolManager()
        req = pool.urlopen('POST', url_statink_v1_battle,
                           headers=http_headers,
                           body=mp_payload,
                           )

        if self.show_response_enabled:
            print(req.data.decode('utf-8'))

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

        # 戦績画面はこの後にくるはずなので今までにあるデータは捨てる
        self.img_result_detail = None
        self.img_judge = None

        IkaUtils.dprint('%s: Discarded screenshots' % self)

    ##
    # on_game_individual_result Hook
    # @param self      The Object Pointer
    # @param context   IkaLog context
    #
    def on_game_individual_result(self, context):
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
        if ('msec' in context['engine']) and (self.time_start_at_msec is not None):
            event_msec = context['engine']['msec'] - self.time_start_at_msec
            self.events.append({
                'type': 'killed',
                'at': event_msec / 1000,
            })

    def on_game_dead(self, context):
        if ('msec' in context['engine']) and (self.time_start_at_msec is not None):
            event_msec = context['engine']['msec'] - self.time_start_at_msec
            self.events.append({
                'type': 'dead',
                'at': event_msec / 1000,
            })

    def on_game_paint_score_update(self, context):
        score = context['game'].get('paint_score', 0)
        if (score > 0 and 'msec' in context['engine']) and (self.time_start_at_msec is not None):
            event_msec = context['engine']['msec'] - self.time_start_at_msec
            # 前回のスコアイベントから 200ms 経っていない場合は処理しない
            if (self.time_last_score_msec is None) or (event_msec - self.time_last_score_msec >= 200):
                # IkaUtils.dprint('%s: score=%d at %.3f' % (self, score, event_msec / 1000))
                self.events.append({
                    'type': 'point',
                    'point': score,
                    'at': event_msec / 1000,
                })
                self.time_last_score_msec = event_msec

    def on_game_objective_position_update(self, context):
        event_msec = context['engine']['msec'] - self.time_start_at_msec

        if (self.time_last_objective_msec is None) or (event_msec - self.time_last_objective_msec >= 200):
            self.events.append({
                'type': 'objective',
                'position': context['game']['tower'].get('pos', 0),
                'at': event_msec / 1000,
            })
            self.time_last_objective_msec = event_msec


    def __init__(self, api_key=None, debug=False, dry_run=False):
        self.enabled = not (api_key is None)
        self.api_key = api_key
        self.dry_run = dry_run

        self.time_start_at = None
        self.time_end_at = None
        self.time_start_at_msec = None

        self.events = []
        self.time_last_score_msec = None
        self.time_last_objective_msec = None

        self.img_result_detail = None
        self.img_judge = None

        self.debug_writePayloadToFile = debug
        self.show_response_enabled = debug

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
