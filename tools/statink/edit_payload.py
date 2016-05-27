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
#  Modifier of payload files for stat.ink
#  Usage:
#    ./tools/statink/edit_payload.py --input statink.msgpack --map=hokke

import argparse
import os
import sys
import umsgpack

# Append the Ikalog root dir to sys.path to import IkaUtils.
sys.path.append(os.path.join(os.path.dirname(__file__), '..', '..'))
from ikalog.constants import rules, stages, udemae_strings, weapons

LOBBY_LIST = [
  'DELETE',
  'standard',  # 通常モード（いわゆる「野良」またはレギュラーフレンド合流）
  'squad_2',  # タッグマッチ（2人タッグ）
  'squad_3',  # タッグマッチ（3人タッグ）
  'squad_4',  # タッグマッチ（4人タッグ）
  'private',  # プライベートマッチ
  'fest',  # フェス(similar to standard)
]
RESULT_LIST = ['DELETE', 'win', 'lose']

RULE_LIST = ['DELETE'] + list(rules.keys())
MAP_LIST = ['DELETE'] + list(stages.keys())
WEAPON_LIST = ['DELETE'] + list(weapons.keys())
RANK_LIST = ['DELETE'] + udemae_strings


def get_args():
    parser = argparse.ArgumentParser()
    parser.add_argument('--input', type=str, required=True)
    parser.add_argument('--output', type=str)
    parser.add_argument('--lobby', choices=LOBBY_LIST)
    parser.add_argument('--rule', choices=RULE_LIST)
    parser.add_argument('--map', choices=MAP_LIST)
    parser.add_argument('--weapon', choices=WEAPON_LIST)
    parser.add_argument('--result', choices=RESULT_LIST)
    parser.add_argument('--kill', type=int)
    parser.add_argument('--death', type=int)
    parser.add_argument('--rank', choices=RANK_LIST)
    parser.add_argument('--rank_exp', type=int,
                        choices=range(0, 100), metavar='[0 - 99]')
    parser.add_argument('--rank_after', choices=RANK_LIST)
    parser.add_argument('--rank_exp_after', type=int,
                        choices=range(0, 100), metavar='[0 - 99]')
    parser.add_argument('--link_url', type=str)

    return vars(parser.parse_args())


def main():
    args = get_args()
    with open(args['input'], 'rb') as f:
        payload = umsgpack.unpack(f)

    keys = ['lobby', 'rule', 'map', 'weapon', 'result', 'kill', 'death',
            'rank', 'rank_exp', 'rank_after', 'rank_exp_after', 'link_url']
    for key in keys:
        value = args.get(key)
        if not value:
            continue
        if value == 'DELETE':
            prev_value = payload.pop(key)
        else:
            prev_value = payload.get(key, '')
            payload[key] = args[key]
        print('Modified %s : %s -> %s' % (key, str(prev_value), str(value)))

    output = args.get('output') or args['input']
    with open(output, 'wb') as f:
        umsgpack.pack(payload, f)


if __name__ == '__main__':
    main()
