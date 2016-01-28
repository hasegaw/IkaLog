#!/usr/bin/env python3
# -*- coding: utf-8 -*-
#
#  IkaLog
#  ======
#  Copyright (C) 2015 Takeshi HASEGAWA, Junki MIZUSHIMA
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

import platform
import re
from subprocess import Popen, PIPE

def __get_ikalog_revision():
    try:
        commit_id = Popen(['git', 'rev-parse', '--short', 'HEAD'], stdout=PIPE).communicate()[0].decode('utf-8')
        version = re.sub(r'\s+', r'', commit_id)
        if version == '':
            return 'unknown'
        return version
    except:
        return 'unknown'

def __get_ikalog_version():
    return '%s (%s)' % (__get_ikalog_revision(), platform.system())

IKALOG_VERSION =  __get_ikalog_version()

if __name__ == '__main__':
    print(IKALOG_VERSION)
