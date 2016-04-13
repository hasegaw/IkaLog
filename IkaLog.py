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

import argparse
import signal
from ikalog.engine import *
from IkaConfig import *
from ikalog.utils import *



def signal_handler(num, frame):
    IkaUtils.dprint('IkaLog: got signal %d' % num)
    if num == 2:
        engine.stop()

def get_args():
    parser = argparse.ArgumentParser()
    parser.add_argument('--input_file', '-f', dest='input_file', type=str)
    parser.add_argument('--output_description', '--desc',
                        dest='output_description', type=str)
    parser.add_argument('--profile', dest='profile', action='store_true',
                        default=False)
    parser.add_argument('--time', '-t', dest='time', type=str)
    parser.add_argument('--time_msec', dest='time_msec', type=int)
    parser.add_argument('--video_id', dest='video_id', type=str)

    return vars(parser.parse_args())

def time_to_msec(time):
    minute, sec = time.split(':')
    return (int(minute) * 60 + int(sec)) * 1000

if __name__ == "__main__":
    signal.signal(signal.SIGINT, signal_handler)

    args = get_args()
    capture, OutputPlugins = IkaConfig().config(args)

    if isinstance(capture, inputs.CVFile):
        pos_msec = args.get('time_msec') or time_to_msec(args.get('time') or '0:0')
        if pos_msec:
            capture.video_capture.set(cv2.CAP_PROP_POS_MSEC, pos_msec)

    engine = IkaEngine(enable_profile=args.get('profile'))
    engine.pause(False)
    engine.set_capture(capture)
    engine.set_plugins(OutputPlugins)
    engine.close_session_at_eof = True
    engine.run()
    IkaUtils.dprint('bye!')
