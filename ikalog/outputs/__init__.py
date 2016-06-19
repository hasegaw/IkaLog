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

from .console import Console
from .csv import CSV
from .debug import DebugLog
from .debug_video_writer import DebugVideoWriter
from .description import Description
from .fluentd import Fluentd
from .hue import Hue
from .webserver.server import RESTAPIServer
from .printjson import JSON
from .preview import Screen
from .preview_detected import PreviewDetected
from .screenshot import Screenshot
from .slack import Slack
from .statink import StatInk
from .switcher import Switcher
from .twitter import Twitter
from .videorecorder import OBS
from .weapon_training import WeaponTraining
from .gearpower_training import GearpowerTraining
from .websocket_server import WebSocketServer
from .boyomi import Boyomi
from .mikumikumouth import MikuMikuMouth

from .osx.say import Say
