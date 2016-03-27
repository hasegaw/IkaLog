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

class Description(object):
    def __init__(self, output_filepath):
        self._description = ""
        self._session_active = True
        self._output_filepath = output_filepath

    def on_game_session_end(self, context):
        summary = "IKA"
        with open(self._output_filepath, 'w') as datafile:
          datafile.write(summary + '\n\n')
          datafile.write(self._description)
        self._session_active = False

    def on_game_session_abort(self, context):
        if self._session_active:
          self.on_game_session_end(context)
