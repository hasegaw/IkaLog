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
import os
import re
import sys
import urllib3
from subprocess import Popen, PIPE

# Append the Ikalog root dir to sys.path to import Certifi.
sys.path.append(os.path.join(os.path.dirname(__file__), '..'))
from ikalog.utils import Certifi

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
    return '%s (%s %s)' % (__get_ikalog_revision(), platform.system(), platform.machine())

def get_latest_versions():
    '''Returns the latest downloadable versions from the web site.'''
    version_dict = {}

    url = 'http://hasegaw.github.io/IkaLog/'
    pool = urllib3.PoolManager(cert_reqs='CERT_REQUIRED',
                               ca_certs=Certifi.where(),
                               timeout=120.0)

    lines = pool.urlopen('GET', url).data.decode('utf-8').split('\n')
    for line in lines:
        if 'IKALOG_VERSION' not in line:
            continue
        items = line.split(' ')
        for i in range(len(items) - 1):
            if 'IKALOG_VERSION' in items[i]:
                version_dict[items[i]] = items[i + 1]

    return version_dict

IKALOG_VERSION =  __get_ikalog_version()
GAME_VERSION = '2.8.0'
GAME_VERSION_DATE = '2016-06-08_04'

SPL2_GAME_VERSION = '1.0.0'
GAME_VERSION_DATE = '2017-07-21_01'


if __name__ == '__main__':
    print(IKALOG_VERSION)
    print(get_latest_versions())
