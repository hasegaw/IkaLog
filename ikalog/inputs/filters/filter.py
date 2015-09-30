#!/usr/bin/env python3
# -*- coding: utf-8 -*-
#
#  IkaLog
#  ======
#  Copyright (C) 2015 Hiromichi Itou
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

class filter:

    def enable(self):
        self.enabled = True

    def disable(self):
        self.enabled = True

    # フィルタをスキップしてもいいとフィルタが思っていたら False
    # フィルタが出力画像をいじる気まんまんなら True を返してください
    def pre_execute(self, frame):
        return True

    def execute(self, frame):
        raise('Please override execute().')

    def __init__(self, parent, debug=False):
        self.parent = parent
        self.disable()
        self.reset()
        self.enabled = False
