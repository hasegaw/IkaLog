#!/usr/bin/env python3
# -*- coding: utf-8 -*-
#
#  IkaLog
#  ======
#  Copyright (C) 2015 ExceptionError
#  Copyright (C) 2015 Takeshi HASEGAWA
#  Copyright (C) 2015 AIZAWA Hina
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
import threading
import time

from ikalog.constants import *
from ikalog.plugin import IkaLogPlugin
from ikalog.utils import *


class SayThread(object):

    def worker_func(self):
        while not self._shutdown:
            if (len(self._msg_queue) == 0):
                time.sleep(0.1)
                continue

            msg = self._msg_queue.pop(0)
            # FixMe: sanitize the input
            cmd = 'say -v Kyoko ' + msg
            print(cmd)
            os.system(cmd)

    def queue_message(self, msg):
        self._msg_queue.append(msg)

    def __init__(self):
        self._msg_queue = []
        self._shutdown = False
        self.worker_thread = threading.Thread(
            target=self.worker_func, )
        self.worker_thread.daemon = True
        self.worker_thread.start()


class SayPlugin(IkaLogPlugin):
    def on_validate_configuration(self, config):
        return True

    def on_reset_configuration(self):
        pass

    def on_set_configuration(self, config):
        pass

    def __init__(self):
        super(SayPlugin, self).__init__()
        self._say_thread = SayThread()

    def _say(self, text, voice=None):
        # print(text)
        self._say_thread.queue_message(text)

#    def on_lobby_matching(self, context):
#        self._say('Awaiting at the lobby')

#    def on_lobby_matched(self, context):
#        self._say('The game will start very soon')

    def on_game_start(self, context):
        stage_text = IkaUtils.map2text(
            context['game']['map'], unknown='スプラトゥーン')
        rule_text = IkaUtils.rule2text(context['game']['rule'], unknown='バトル')
        self._say('%(stage) で %(rule)s がはじまります' %
                  {'rule': rule_text, 'stage': stage_text})

    def on_game_special_weapon(self, context, params={}):
        print("on_game_special_weapon", params)
        prefix = '自分の' if params.get('is_my_special_weapon', False) else '味方の'
        special_weapon_id = params.get('special_weapon')
        special_weapon = special_weapons.get(special_weapon_id, {})
        special_weapon_text = special_weapon.get('ja_JP', None)
        print('special_weapon_id', special_weapon_id, 'special_weapon',
              special_weapon, 'text', special_weapon_text)

        if not special_weapon_text:
            return

        self._say('%s %s' % (prefix, special_weapon_text))

    def on_game_killed(self, context, params=None):
        #        self._say('Splatted someone!')
        self._say('たおした', voice='Kyoko')

    def on_game_dead(self, context, params=None):
        #        self._say('You were splatted!')
        self._say('やられた', voice='Kyoko')

    def on_game_splatzone_we_got(self, context, params=None):
        self._say('エリアを確保した')

    def on_game_splatzone_we_lost(self, context, params=None):
        self._say('エリアを失った')

    def on_game_splatzone_they_got(self, context, params=None):
        self._say('エリアを確保された')

    def on_game_splatzone_they_lost(self, context, params=None):
        self._say('エリアを取り戻した')

    def on_game_rainmaker_we_got(self, context, params=None):
        self._say('ホコを確保した')

    def on_game_rainmaker_we_lost(self, context, params=None):
        self._say('ホコを失った')

    def on_game_rainmaker_they_got(self, context, params=None):
        self._say('ホコを確保された')

    def on_game_rainmaker_they_lost(self, context, params=None):
        self._say('ホコを取り戻した')

    def on_game_towercontrol_we_took(self, context, params=None):
        self._say('ヤグラを確保した')

    def on_game_towercontrol_we_lost(self, context, params=None):
        self._say('ヤグラを失った')

    def on_game_towercontrol_they_took(self, context, params=None):
        self._say('ヤグラを確保された')

    def on_game_towercontrol_they_lost(self, context, params=None):
        self._say('ヤグラを取り戻した')

    def on_game_ranked_we_lead(self, context, params=None):
        self._say('カウントリードした')

    def on_game_ranked_they_lead(self, context, params=None):
        self._say('カウントリードされた')

    def on_game_death_reason_identified(self, context, params=None):
        reason = context['game']['last_death_reason']
        if reason in oob_reasons:
            self._say('おちた', voice='Kyoko')
#            self._say('Out ob bound')
        else:
            weapon = cause_of_death_v2.get(reason)
            weapon_text = weapon.get('name', {}).get('ja_JP', reason)
            self._say("%s でやられた" % weapon_text, voice='Kyoko')
#            self._say('%(weapon)s' % {'weapon': weapon_text})


class Say(SayPlugin):

    def __init__(self, dest_dir=None):
        super(Say, self).__init__()

        config = self.get_configuration()
        config['dest_dir'] = dest_dir
        config['enabled'] = True
        self.set_configuration(config)
