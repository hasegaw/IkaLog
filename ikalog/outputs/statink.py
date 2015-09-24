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

# @package IkaOutput_Twitter


from datetime import datetime
import os
import pprint

from ikalog.utils import *

# IkaLog Output Plugin for Stat.ink

class statink:

    # serializePayload
    def serializePayload(self, context):
        payload = {}

        payload['result'] = IkaUtils.getWinLoseText( context['game']['won'], win_text='win', lose_text='lose', unknown_text=None)
        if payload['result'] is None:
            del payload['result']

        t = datetime.now().strftime("%Y/%m/%d %H:%M")
        try:
            payload['map'] = {
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
            IkaUtils.dprint('%s: Failed convert map stas.ink value' % self)

        try:
            payload['rule'] = {
                'ナワバリバドル': 'nawabari',
                'ガチエリア': 'area',
                'ガチヤグラ': 'yagura',
                'ガチホコバトル': 'hoko',
            }[IkaUtils.rule2text(context['game']['rule'])]
        except:
            IkaUtils.dprint('%s: Failed convert rule to stas.ink value' % self)

        me = IkaUtils.getMyEntryFromContext(context)
        payload['rank_in_team'] = me['rank_in_team']

        if ('kills' in me) and ('deaths' in me):
            payload['kill'] = me['kills']
            payload['death'] = me['deaths']

        if ('udemae_pre' in me):
            payload['udemae'] = me['udemae_pre'].lower()

        if IkaUtils.isWindows():
            temp_file = os.path.join(
                os.environ['TMP'], '_image_for_statink2.png')
        else:
            temp_file = '_image_for_statink2.png'

        try:
            # ToDo: statink accepts only 16x9
            # Memo: This function will be called from onGameIndividualResult,
            #       therefore context['engine']['frame'] should have a result.
            IkaUtils.writeScreenshot(temp_file, context['engine']['frame'])
            f = open(temp_file, 'rb')
            payload['image_result'] = f.read()
            try:
                f.close()
                os.remove(temp_file)
            except:
                pass
        except:
            IkaUtils.dprint('%s: Failed to attach image_result' % self)

        return payload

    def onGameIndividualResult(self, context):
        IkaUtils.dprint('%s (enabled = %s)' % (self, self.enabled))

        if not self.enabled:
            return False

        payload = self.serializePayload(context)
        if 'image_result' in payload:
            payload['image_result'] = '(PNG Data)'
        pprint.pprint(payload)

    def checkImport(self):
        try:
            from requests_oauthlib import OAuth1Session
        except:
            print("モジュール requests_oauthlib がロードできませんでした。 Twitter 投稿ができません。")
            print("インストールするには以下のコマンドを利用してください。\n    pip install requests_oauthlib\n")

    def __init__(self, enabled=True):
        self.enabled = enabled
        self.checkImport()
