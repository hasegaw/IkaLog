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
stop_requested = False

def signal_handler(num, frame):
    IkaUtils.dprint('IkaLog: got signal %d' % num)
    if num == 2:
        stop_requested = True

signal.signal(signal.SIGINT, signal_handler)

# Source
source = inputs.CVFile()
source.start_video_file(sys.argv[1])

consolidated_source = inputs.ConsolidatedInput(source)

# Engine
engines = []
for view in consolidated_source.outputs:
    engine = IkaEngine()
    engines.append(engine)
    engine.pause(False)
    engine.set_capture(view)
    engine.set_plugins([
        outputs.Console()
    ])
    engine.close_session_at_eof = False

# Main loop

while not stop_requested:
    consolidated_source.next_frame()

    for engine in engines:
        engine.process_frame()

    cv2.waitKey(1)


#capture, OutputPlugins = IkaConfig().config()
IkaUtils.dprint('bye!')
