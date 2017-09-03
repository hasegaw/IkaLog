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

from ikalog.scenes.scene import Scene
from ikalog.utils import *
import re


class StatefulScene(Scene):

    def _switch_state(self, new_state):
        self._state = new_state

        if self._disable_state_message:
            return

        scene_name = str(self)
        m = re.match(r'<ikalog\.scenes.*\.([a-zA-Z0-9_]+) object at ([a-f0-9]+)', scene_name)
        if m:
            scene_name = '<%s>' % (m.group(1))

        IkaUtils.dprint('%s: new state %s' %
                        (scene_name, new_state.__name__))

    def _state_default(self, context):
        raise Exception('Must be overrided')

    def match_no_cache(self, context):
        return self._state(context)

    def __init__(self, engine):
        super(StatefulScene, self).__init__(engine)

        self._state = self._state_default
        self._disable_state_message = False
