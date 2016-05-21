#!/usr/bin/env python3
# -*- coding: utf-8 -*-
#
#  IkaLog
#  ======
#  Copyright (C) 2016 Takeshi HASEGAWA
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
#  tools/print_data.py is a command to print out data analyzed by IkaLog.
#  Usage:
#    ./tools/print_data.py --json ika.json
#    ./tools/print_data.py --statink statink.msgpack

import argparse
import json
import os
import pprint
import sys
import time
import umsgpack

# Append the Ikalog root dir to sys.path to import IkaUtils.
sys.path.append(os.path.join(os.path.dirname(__file__), '..'))
from ikalog.utils.statink_uploader import UploadToStatInk
from ikalog.utils.ikautils import IkaUtils


def get_args():
    parser = argparse.ArgumentParser()
    parser.add_argument('--statink', dest='statink', type=str)
    parser.add_argument('--json', dest='json', type=str)

    return vars(parser.parse_args())


def print_statink(filepath):
    with open(filepath, 'rb') as data:
      payload = umsgpack.unpack(data)

    if 'image_result' in payload:
        payload['image_result'] = '(PNG Data)'

    if 'image_judge' in payload:
        payload['image_judge'] = '(PNG Data)'

    if 'image_gear' in payload:
        payload['image_gear'] = '(PNG Data)'

    if 'events' in payload:
        payload['events'] = '(Events)'

    pprint.pprint(payload)


def print_json(filepath):
    with open(filepath, 'r') as data:
        for line in data:
            if not line.rstrip():
                continue
            json_data = json.loads(line)
            print(json.dumps(json_data, sort_keys=True, ensure_ascii=False,
                             indent=2, separators=(',', ': ')))


def main():
    args = get_args()
    if args.get('statink'):
        print_statink(args['statink'])
    elif args.get('json'):
        print_json(args['json'])

if __name__ == '__main__':
    main()
