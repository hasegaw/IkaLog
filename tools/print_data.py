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
#    ./tools/print_data.py --tsv --json ika.json
#    ./tools/print_data.py --tsv --tsv_format reslut,kill,death --json ika.json

import argparse
import json
import os
import os.path
import pprint
import sys
import time
import umsgpack

# Append the Ikalog root dir to sys.path to import IkaUtils.
sys.path.append(os.path.join(os.path.dirname(__file__), '..'))
from ikalog.utils.ikautils import IkaUtils

FORMAT_DICT = {
    'TEXT': ('end_at_text,lobby_text,rule_text,map_text,weapon_text,'
             'result,kill,death,rank_before,rank_after'),
    'ID': ('end_at,lobby,rule,map,weapon,'
           'result,kill,death,rank_before,rank_after')
}

def get_args():
    parser = argparse.ArgumentParser(
        description='Output stat.ink payload/JSON file in human readable format.'
    )

    group = parser.add_mutually_exclusive_group()
    group.add_argument('--statink', dest='statink',
                       metavar='STATINK_PAYLOAD_FILE', type=str)
    group.add_argument('--json', dest='json', metavar='JSON_FILE', type=str)
    parser.add_argument('--tsv', action='store_true', default=False)
    parser.add_argument('--tsv_format', type=str, default=FORMAT_DICT['TEXT'],
                        help='format separated by commna, otherwise TEXT or ID')

    return vars(parser.parse_args())


def _get_lobby_id(statink_lobby):
    lobby_dict = {
        'standard': 'public',
        'private': 'private',
        'fest': 'festa',
        'squad_2': 'tag',
        'squad_3': 'tag',
        'squad_4': 'tag',
    }
    return lobby_dict.get(statink_lobby, '')


def print_tsv(summary, tsv_format):
    summary = summary.copy()
    summary['end_at_text'] = time.strftime('%Y-%m-%d %H:%M:%S',
                                           time.localtime(summary['end_at']))
    summary['lobby_text'] = IkaUtils.lobby2text(_get_lobby_id(summary['lobby']),
                                                unknown='')
    summary['rule_text'] = IkaUtils.rule2text(summary['rule'], unknown='')
    summary['map_text'] = IkaUtils.map2text(summary['map'], unknown='')
    summary['weapon_text'] = IkaUtils.weapon2text(summary['weapon'], unknown='')

    keys = tsv_format.split(',')
    values = []
    for key in keys:
        values.append(str(summary[key]))
    print('\t'.join(values))


def get_statink_summary(payload):
    summary = {}
    summary['end_at'] = payload['end_at']
    summary['lobby'] = payload.get('lobby', '')
    summary['rule'] = payload.get('rule', '')
    summary['map'] = payload.get('map', '')
    summary['result'] = payload.get('result', '')
    summary['kill'] = payload.get('kill', '')
    summary['death'] = payload.get('death', '')
    summary['weapon'] = payload.get('weapon', '')
    summary['rank_before'] = (payload.get('rank', '') +
                              str(payload.get('rank_exp', '')))
    summary['rank_after'] = (payload.get('rank_after', '') +
                             str(payload.get('rank_exp_after', '')))
    return summary


def print_statink(filepath, tsv_format=None):
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

    if tsv_format:
        payload_summary = get_statink_summary(payload)
        print_tsv(payload_summary, tsv_format)
    else:
        pprint.pprint(payload)


def get_json_summary(json_data):
    summary = {}
    summary['end_at'] = json_data['time']
    summary['lobby'] = json_data.get('lobby', '')
    rule = json_data.get('rule', '')
    if rule == '?':
        rule = ''
    summary['rule'] = rule
    map_name = json_data.get('map', '')
    if map_name == '?':
        map_name = ''
    summary['map'] = map_name
    result = json_data.get('result', '')
    if result == 'unknown':
        result = ''
    summary['result'] = result
    summary['kill'] = json_data.get('kills', '')
    summary['death'] = json_data.get('deaths', '')
    summary['weapon'] = json_data.get('weapon', '')
    summary['rank_before'] = (json_data.get('udemae_pre', '') +
                              str(json_data.get('udemae_exp_pre', '')))
    summary['rank_after'] = (json_data.get('udemae_after', '') +
                             str(json_data.get('udemae_exp_after', '')))
    return summary


def print_json(filepath, tsv_format=None):
    with open(filepath, 'r') as data:
        for line in data:
            if not line.rstrip():
                continue
            json_data = json.loads(line)
            if tsv_format:
                json_summary = get_json_summary(json_data)
                print_tsv(json_summary, tsv_format)
            else:
                pprint.pprint(json_data)


def main():
    args = get_args()
    tsv_format = None
    if args.get('tsv'):
        # Set the corresponding value of FORMAT_DICT, or tsv_format itself.
        tsv_format = FORMAT_DICT.get(args['tsv_format'], args['tsv_format'])

    if args.get('statink'):
        print_statink(args['statink'], tsv_format)
    elif args.get('json'):
        print_json(args['json'], tsv_format)

if __name__ == '__main__':
    main()
