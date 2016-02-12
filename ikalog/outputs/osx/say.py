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
from ikalog.utils import *


class SayThread(object):

    def worker_func(self):
        while not self._shutdown:
            if (len(self._msg_queue) == 0):
                time.sleep(0.1)
                continue

            msg = self._msg_queue.pop(0)
            # FixMe: sanitize the input
            cmd = 'say ' + msg
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


class Say(object):

    def __init__(self):
        self._say_thread = SayThread()

    def _say(self, text):
        # print(text)
        self._say_thread.queue_message(text)

    def on_lobby_matching(self, context):
        self._say('Awaiting at the lobby')

    def on_lobby_matched(self, context):
        self._say('The game will start very soon')

    def on_game_start(self, context):
        stage_text = IkaUtils.map2text(
            context['game']['map'], unknown='Splatoon')
        rule_text = IkaUtils.rule2text(context['game']['rule'], unknown='The')
        self._say('%(rule)s game starts at %(stage)s' %
                  {'rule': rule_text, 'stage': stage_text})

    def on_game_killed(self, context):
        self._say('Splatted someone!')

    def on_game_dead(self, context):
        self._say('You were splatted!')

    def on_game_death_reason_identified(self, context):
        reason = context['game']['last_death_reason']
        if reason in oob_reasons:
            self._say('Out ob bound')
        else:
            weapon_text = weapons.get(reason, {}).get('en', reason)
            self._say('%(weapon)s' % {'weapon': weapon_text})

    def on_game_special_weapon(self, context):
        special_weapon = context['game']['special_weapon']
        special_weapon_text = special_weapons.get(special_weapon, {}).get('en', special_weapon)

        if context['game']['special_weapon_is_mine']:
            special_weapon_text = 'my %s' % special_weapon_text
        else:
            special_weapon_text = 'team %s' % special_weapon_text

        self._say('%(special_weapon)s' % {'special_weapon': special_weapon_text})
