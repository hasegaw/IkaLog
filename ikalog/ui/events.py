#!/usr/bin/env python3
# -*- coding: utf-8 -*-
#
#  IkaLog
#  ======
#  Copyright (C) 2015 Takeshi HASEGAWA
#  Copyright (C) 2016 Hiroyuki KOMATSU
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

import wx
import wx.lib.newevent

# New input file is entered. (see: PreviewPanel.on_input_file_button_click)
(InputFileAddedEvent, EVT_INPUT_FILE_ADDED) = wx.lib.newevent.NewEvent()

# New input source is initialized. (see: VideoCapture.initialize_input)
(InputInitializedEvent, EVT_INPUT_INITIALIZED) = wx.lib.newevent.NewEvent()
