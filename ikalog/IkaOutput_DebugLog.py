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

from .IkaUtils import *


# IkaLog Output Plugin: Write debug logs.


class IkaOutput_DebugLog:

    def writeDebugLog(self, event, context):
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

    def onFrameReadFailed(self, context):
        pass

    def onGameKilled(self, context):
        self.writeDebugLog(sys._getframe().f_code.co_name, context)

    def onGameDead(self, context):
        self.writeDebugLog(sys._getframe().f_code.co_name, context)

    def onGameGoSign(self, context):
        self.writeDebugLog(sys._getframe().f_code.co_name, context)

    def onGameStart(self, context):
        self.writeDebugLog(sys._getframe().f_code.co_name, context)

    def onGameTeamColor(self, context):
        self.writeDebugLog(sys._getframe().f_code.co_name, context)

    def onLobbyMatching(self, context):
        self.writeDebugLog(sys._getframe().f_code.co_name, context)

    def onLobbyMatched(self, context):
        self.writeDebugLog(sys._getframe().f_code.co_name, context)

    def onGameFinish(self, context):
        self.writeDebugLog(sys._getframe().f_code.co_name, context)

    def onGameIndividualResult(self, context):
        self.writeDebugLog(sys._getframe().f_code.co_name, context)

    def __init__(self, dir='debug/', screenshot=False):
        self.dir = dir
        self.screenshot = screenshot
