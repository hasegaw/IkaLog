#!/usr/bin/env python3
# -*- coding: utf-8 -*-
#
#  IkaLog
#  ======
#  Copyright (C) 2016 Takeshi HASEGAWA
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

import argparse
import os
import sys
import umsgpack

# Append the Ikalog root dir to sys.path to import IkaUtils.
sys.path.append(os.path.join(os.path.dirname(__file__), '..', '..'))
import IkaConfig
from ikalog.utils.statink_uploader import UploadToStatInk


def get_args():
    parser = argparse.ArgumentParser()
    parser.add_argument('--payload', dest='payload', type=str)
    parser.add_argument('--api_key', dest='api_key', type=str)
    parser.add_argument('--video_id', dest='video_id', type=str)

    return vars(parser.parse_args())


def main():
    args = get_args()
    f = open(args['payload'], 'rb')
    payload = umsgpack.unpack(f)
    f.close()
    url = 'https://stat.ink/api/v1/battle'
    api_key = (args['api_key'] or IkaConfig.OUTPUT_ARGS['StatInk']['api_key'])
    error, response = UploadToStatInk(payload, api_key, url, args['video_id'])
    print(response.get('url'))

if __name__ == '__main__':
    main()
