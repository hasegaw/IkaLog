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

import signal

from ikalog.engine import *
from IkaConfig import *
from ikalog.utils import *
from hdmi_switcher import HDMISwitcher
import time


class IkaLog4(object):

    def signal_handler(num, frame):
        IkaUtils.dprint('IkaLog: got signal %d' % num)
        if num == 2:
            self.stop_requested = True

    def context2view(self, context):
        for n in range(len(self.engines)):
            if self.engines[n].context == context:
                return n + 1
        return None

    def switch_to_single(self, port):
        self.switcher.cmd_switch_port(port)
        time.sleep(0.1)
        self.switcher.cmd_mode(self.switcher.mode_single_channel)
        self.consolidated_source.config_720p_single(port)

    def switch_to_quad(self, port=None):
        self.switcher.cmd_mode(self.switcher.mode_four_channels)
        time.sleep(0.1)
        if port is not None:
            self.switcher.cmd_switch_port(1)
        self.consolidated_source.config_720p_quad()

    def initialize_switcher(self, f):
        self.switcher = HDMISwitcher('/dev/tty.usbserial-FTZ2AKZU')
        time.sleep(1)
        self.switcher.cmd_resolution(self.switcher.res_720p)
        time.sleep(1)

        self.switch_to_quad()

    def initialize_sources(self):
        try:
            f = sys.argv[1]
            source = inputs.CVFile()
            source.start_video_file(f)
        except:
            source = inputs.AVFoundationCapture()
            source.start_camera(1)

        self.consolidated_source = inputs.ConsolidatedInput(source)

    def initialize_engines(self):
        # Engine
        self.engines = []
        for view in self.consolidated_source.outputs:
            engine = IkaEngine()
            engine.pause(False)
            engine.set_capture(view)
            engine.set_plugins([
                # outputs.Console(),
                outputs.DebugLog(),
                self,
            ])
            engine.close_session_at_eof = False

            self.engines.append(engine)

    def main_loop(self):

        while not self.stop_requested:
            self.consolidated_source.next_frame()

            for engine in self.engines:
                engine.process_frame()

            cv2.waitKey(1)
        IkaUtils.dprint('bye!')

    def on_lobby_matching(self, context):
        print('on_lobby_matching', self.context2view(context))
        self.switch_to_quad()

    def on_lobby_matched(self, context):
        print('on_lobby_matched', self.context2view(context))
        self.switch_to_single(self.context2view(context))

    def on_game_start(self, context):
        print('on_game_start', self.context2view(context))

    def on_game_go_sign(self, context):
        print('on_game_go_sign', self.context2view(context))
        self.switch_to_quad()

    def on_game_finish(self, context):
        print('on_game_finish', self.context2view(context))
        self.switch_to_single(self.context2view(context))

    def on_result_gears(self, context):
        self.switch_to_quad()

    def __init__(self):
        self.stop_requested = False
        signal.signal(signal.SIGINT, self.signal_handler)


ikalog4 = IkaLog4()
sources = ikalog4.initialize_sources()
ikalog4.initialize_engines()
ikalog4.initialize_switcher('')
ikalog4.main_loop()
