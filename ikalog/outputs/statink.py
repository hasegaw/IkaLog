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
import os
import pprint
import urllib3
import msgpack
import traceback

from ikalog.utils import *

# Needed in GUI mode
try:
    import wx
except:
    pass

# @package ikalog.outputs.statink

# IkaLog Output Plugin for Stat.ink


class statink:

    def ApplyUI(self):
        self.enabled = self.checkEnable.GetValue()
        self.api_key = self.editApiKey.GetValue()

    def RefreshUI(self):
        self.checkEnable.SetValue(self.enabled)

        if not self.api_key is None:
            self.editApiKey.SetValue(self.api_key)
        else:
            self.editApiKey.SetValue('')

    def onConfigReset(self, context=None):
        self.enabled = False
        self.api_key = None

    def onConfigLoadFromContext(self, context):
        self.onConfigReset(context)
        try:
            conf = context['config']['stat.ink']
        except:
            conf = {}

        if 'Enable' in conf:
            self.enabled = conf['Enable']

        if 'APIKEY' in conf:
            self.api_key = conf['APIKEY']

        self.RefreshUI()
        return True

    def onConfigSaveToContext(self, context):
        context['config']['stat.ink'] = {
            'Enable': self.enabled,
            'APIKEY': self.api_key,
        }

    def onConfigApply(self, context):
        self.ApplyUI()

    def onOptionTabCreate(self, notebook):
        self.panel = wx.Panel(notebook, wx.ID_ANY)
        self.page = notebook.InsertPage(0, self.panel, 'stat.ink')
        self.layout = wx.BoxSizer(wx.VERTICAL)
        self.panel.SetSizer(self.layout)
        self.checkEnable = wx.CheckBox(
            self.panel, wx.ID_ANY, u'stat.ink へのスコアを送信する')
        self.editApiKey = wx.TextCtrl(self.panel, wx.ID_ANY, u'hoge')

        self.layout.Add(self.checkEnable)
        self.layout.Add(wx.StaticText(
            self.panel, wx.ID_ANY, u'APIキー'))
        self.layout.Add(self.editApiKey, flag=wx.EXPAND)

        self.panel.SetSizer(self.layout)

    def encodeStageName(self, context):
        try:
            return {
                'アロワナモール': 'arowana',
                'Bバスパーク': 'bbass',
                'デカライン高架下': 'dekaline',
                'ハコフグ倉庫': 'hakofugu',
                'ヒラメが丘団地': 'hirame',
                'ホッケふ頭': 'hokke',
                'マサバ海峡大橋': 'masaba',
                'モンガラキャンプ場': 'mongara',
                'モズク農園': 'mozuku',
                'ネギトロ炭鉱': 'negitoro',
                'シオノメ油田': 'shionome',
                'タチウオパーキング': 'tachiuo'
            }[IkaUtils.map2text(context['game']['map'])]
        except:
            IkaUtils.dprint(
                '%s: Failed convert staage name to stas.ink value' % self)
            return None

    def encodeRuleName(self, context):
        try:
            return {
                'ナワバリバドル': 'nawabari',
                'ガチエリア': 'area',
                'ガチヤグラ': 'yagura',
                'ガチホコバトル': 'hoko',
            }[IkaUtils.rule2text(context['game']['rule'])]
        except:
            IkaUtils.dprint(
                '%s: Failed convert rule name to stas.ink value' % self)
            return None

    def encodeImage(self, img):
        if IkaUtils.isWindows():
            temp_file = os.path.join(
                os.environ['TMP'], '_image_for_statink.png')
        else:
            temp_file = '_image_for_statink.png'

        try:
            # ToDo: statink accepts only 16x9
            # Memo: This function will be called from onGameIndividualResult,
            #       therefore context['engine']['frame'] should have a result.
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

        return s

    # serializePayload
    def serializePayload(self, context):
        payload = {}

        payload['map'] = self.encodeStageName(context)
        payload['rule'] = self.encodeRuleName(context)
        payload['result'] = IkaUtils.getWinLoseText(
            context['game']['won'], win_text='win', lose_text='lose', unknown_text=None)

        if self.time_start_at and self.time_end_at:
            payload['start_at'] = int(self.time_start_at)
            payload['end_at'] = int(self.time_end_at)

        me = IkaUtils.getMyEntryFromContext(context)

        int_fields = [
            # 'type', 'IkaLog Field', 'stat.ink Field'
            ['int', 'rank_in_team', 'rank_in_team'],
            ['int', 'kill', 'kills'],
            ['int', 'death', 'deaths'],
            ['int', 'level', 'rank'],
            ['int', 'my_point', 'score'],
            ['str_lower', 'rank', 'udemae_pre'],
        ]

        for field in int_fields:
            f_type = field[0]
            f_statink = field[1]
            f_ikalog = field[2]
            if (f_ikalog in me):
                if f_type == 'int':
                    try:
                        payload[f_statink] = int(me[f_ikalog])
                    except:  # ValueError
                        IkaUtils.dprint('%s: field %s failed: me[%s] == %s' % (
                            self, f_statink, f_ikalog, me[f_ikalog]))
                        pass
                elif f_type == 'str':
                    payload[f_statink] = str(me[f_ikalog])
                elif f_type == 'str_lower':
                    payload[f_statink] = str(me[f_ikalog]).lower()

        payload['image_result'] = self.encodeImage(context['engine']['frame'])

        payload['agent'] = 'IkaLog'
        payload['agent_version'] = '0.01'

        # Delete any None values
        for field in payload.keys():
            if payload[field] is None:
                del payload[field]

        return payload

    def writeResponseToFile(self, r_header, r_body, basename=None):
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

    def writePayloadToFile(self, payload, basename=None):
        if basename is None:
            t = datetime.now().strftime("%Y%m%d_%H%M")
            basename = os.path.join('/tmp', 'statink_%s' % t)

        try:
            f = open(basename + '.msgpack', 'w')
            f.write(''.join(map(chr, msgpack.packb(payload))))
            f.close()
        except:
            IkaUtils.dprint('%s: Failed to write msgpack file' % self)
            IkaUtils.dprint(traceback.format_exc())

    def postPayload(self, payload, api_key=None):
        url_statink_v1_battle = 'https://stat.ink/api/v1/battle'
        #url_statink_v1_battle = 'http://192.168.44.232:81'

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
        mp_payload_bytes = msgpack.packb(payload)
        mp_payload = ''.join(map(chr, mp_payload_bytes))

        pool = urllib3.PoolManager()
        req = pool.urlopen('POST', url_statink_v1_battle,
                           headers=http_headers,
                           body=mp_payload,
                           )

        print(req.data.decode('utf-8'))

    def printPayload(self, payload):
        payload = payload.copy()

        if 'image_result' in payload:
            payload['image_result'] = '(PNG Data)'
        pprint.pprint(payload)

    def onGameGoSign(self, context):
        self.time_start_at = int(time.time())
        self.time_end_at = None

        # check if context['engine']['msec'] exists
        # to allow unit test.
        if 'msec' in context['engine']:
            self.time_start_at_msec = context['engine']['msec']

    def onGameFinish(self, context):
        self.time_end_at = int(time.time())
        if 'msec' in context['engine']:
            duration_msec = context['engine']['msec'] - self.time_start_at_msec

            if duration_msec >= 0.0:
                self.time_start_at = int(
                    self.time_end_at - int(duration_msec / 1000))

    def onGameIndividualResult(self, context):
        IkaUtils.dprint('%s (enabled = %s)' % (self, self.enabled))

        if not self.enabled:
            return False

        payload = self.serializePayload(context)

        self.printPayload(payload)

        #del payload['image_result']

        if self.debug_writePayloadToFile:
            self.writePayloadToFile(payload)

        self.postPayload(payload)

    def checkImport(self):
        try:
            from requests_oauthlib import OAuth1Session
        except:
            print("モジュール urllib3 がロードできませんでした。 stat.ink 投稿ができません。")
            print("インストールするには以下のコマンドを利用してください。\n    pip install urllib3\n")

    def __init__(self, api_key=None, debug=False):
        self.enabled = not (api_key is None)
        self.api_key = api_key

        self.checkImport()

        self.time_start_at = None
        self.time_end_at = None

        self.debug_writePayloadToFile = debug

if __name__ == "__main__":
    # main として呼ばれた場合
    #
    # 第一引数で指定された戦績画面スクリーンショットを、
    # ハコフグ倉庫・ガチエリアということにして Post する
    #
    # APIキーを環境変数 IKALOG_STATINK_APIKEY に設定して
    # おくこと

    import sys
    from ikalog.scenes.result_detail import *

    obj = statink(
        api_key=os.environ['IKALOG_STATINK_APIKEY'],
        debug=True
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
        },
    }

    # 各プレイヤーの状況を分析
    IkaScene_ResultDetail().analyze(context)

    # stat.ink へのトリガ
    obj.onGameIndividualResult(context)
