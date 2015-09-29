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

    def write_debug_log(self, event, context):
        gt = int(context['engine']['msec'] / 1000)
        mm = '{0:02d}'.format(int(gt / 60))
        ss = '{0:02d}'.format(int(gt % 60))

        # Write to console
        print('[event] %s:%s %s' % (mm, ss, event))

        # Write to screenshot if enabled
        if self.screenshot:
            t = time.localtime()
            time_str = time.strftime("%Y%m%d_%H%M%S", t)
            log_name = '%s_%s_%s.png' % (event, time_str, time.time())
            destfile = os.path.join(self.dir, log_name)
            IkaUtils.writeScreenshot(destfile, context['engine']['frame'])

    def on_frame_read_failed(self, context):
        pass

    def on_game_killed(self, context):
        self.write_debug_log(sys._getframe().f_code.co_name, context)

    def on_game_dead(self, context):
        self.write_debug_log(sys._getframe().f_code.co_name, context)

    def on_game_go_sign(self, context):
        self.write_debug_log(sys._getframe().f_code.co_name, context)

    def on_game_start(self, context):
        self.write_debug_log(sys._getframe().f_code.co_name, context)

    def on_game_team_color(self, context):
        self.write_debug_log(sys._getframe().f_code.co_name, context)

    def on_lobby_matching(self, context):
        self.write_debug_log(sys._getframe().f_code.co_name, context)

    def on_lobby_matched(self, context):
        self.write_debug_log(sys._getframe().f_code.co_name, context)

    def on_game_finish(self, context):
        self.write_debug_log(sys._getframe().f_code.co_name, context)

    def on_game_individual_result(self, context):
        self.write_debug_log(sys._getframe().f_code.co_name, context)

    def __init__(self, dir='debug/', screenshot=False):
        self.dir = dir
        self.screenshot = screenshot
