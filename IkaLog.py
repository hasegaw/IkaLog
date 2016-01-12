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

from ikalog.utils import Localization, IkaUtils
Localization.print_language_settings()

import signal
from ikalog.engine import *
from IkaConfig import *
from ikalog.utils import *


def signal_handler(num, frame):
    IkaUtils.dprint('IkaLog: got signal %d' % num)
    if num == 2:
        engine.stop()

signal.signal(signal.SIGINT, signal_handler)

capture, OutputPlugins = IkaConfig().config()
engine = IkaEngine()
engine.pause(False)
engine.set_capture(capture)
engine.set_plugins(OutputPlugins)
engine.close_session_at_eof = True
engine.run()
IkaUtils.dprint('bye!')
