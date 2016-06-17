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

from ikalog.utils import *


class HDMISwitcherMock(object):
    mode_single_channel = 1
    mode_four_channels = 2
    res_720p = 3

    def cmd_switch_port(self, port):
        pass

    def cmd_mode(self, mode):
        pass

    def cmd_resolution(self, res):
        pass

    def __init__(self, filename):
        pass

def CreateHDMISwitcher(filename):
#    try:
    if 1:
        from hdmi_switcher import HDMISwitcher
        return HDMISwitcher(filename)

#    except:
        IkaUtils.dprint('HDMI Switcher module is not available. Using mock object')
        return HDMISwitcherMock(filename)


class Switcher(object):

    def switch_to_single(self, port=1):
        self.switcher.cmd_switch_port(port)
        time.sleep(0.1)
        self.switcher.cmd_mode(self.switcher.mode_single_channel)

    def switch_to_quad(self, port=None):
        self.switcher.cmd_mode(self.switcher.mode_four_channels)
        time.sleep(0.1)
        if port is not None:
            self.switcher.cmd_switch_port(1)

    def initialize_switcher(self, filename):
        self.switcher = CreateHDMISwitcher(filename)
        time.sleep(1)
        self.switcher.cmd_resolution(self.switcher.res_720p)
        time.sleep(1)

        self.switch_to_quad()

    def on_lobby_matching(self, context):
        self.switch_to_quad()

    def on_lobby_matched(self, context):
        self.switch_to_single()

    def on_game_start(self, context):
        pass

    def on_game_go_sign(self, context):
        self.switch_to_quad()

    def on_game_finish(self, context):
        self.switch_to_single()

    def on_result_gears(self, context):
        self.switch_to_quad()

    def __init__(self, filename):
        self.initialize_switcher(filename)

if __name__ == "__main__":
    pass
