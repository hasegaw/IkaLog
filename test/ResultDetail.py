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

import sys
import json
import argparse
import pprint
import cv2

from ikalog.scenes.result_detail import ResultDetail
from ikalog.utils import IkaUtils


class TestResultDetail:

    # 正解ファイルを作成する
    def answer_filename(self, video_file, answer_type, context):
        #basename_fullpath, ext = os.path.splitext(video_file)
        basename_fullpath = video_file
        answer_fullpath = basename_fullpath + '.answer.' + answer_type
        return answer_fullpath

    def create_record(self, context):
        players = []
        for e in context['game']['players']:
            r = {}

            for field in ['rank', 'kills', 'deaths', 'weapon', 'score', 'udemae_pre']:
                if field in e:
                    r[field] = e[field]

            players.append(r)

        record = {
            'players': players,
            'won': context['game']['won']
        }
        return record

    answer_type = 'ResultDetail'

    # 正解ファイルを作成する
    def write_answer_file(self, video_file, record):
        answer_fullpath = self.answer_filename(
            video_file, self.answer_type, None)

        f = open(answer_fullpath, 'w')
        f.write(json.dumps(record))
        f.close()

        IkaUtils.dprint('wrote answer file %s' % answer_fullpath)
        return True

    def read_answer_file(self, video_file):
        answer_fullpath = self.answer_filename(
            video_file, self.answer_type, None)

        f = open(answer_fullpath, 'r')
        record = json.load(f)
        f.close()
        return record

    def test_regression(self, record, answer):

        assert(answer['won'] == record['won'])

        for n in range(len(record['players'])):
            p = record['players'][n]
            ans_p = answer['players'][n]

            for field in ans_p.keys():
                if str(ans_p[field]) != str(p[field]):
                    raise Exception('player %d key "%s" value "%s" expected "%s"' % (
                        n, field, p[field], ans_p[field]))
        return True

    def remove_images(self, context):
        for e in context['game']['players']:
            for field in e.keys():
                if field.startswith('img_'):
                    e[field] = 'image: %s' % str(e[field].shape)

    def __init__(self, file):
        target = cv2.imread(file)
        cv2.imshow('input', target)

        context = {
            'engine': {'frame': target},
            'game': {},
        }

        obj = ResultDetail()
        matched = obj.match(context)
        analyzed = obj.analyze(context)

        self.remove_images(context)
        record = self.create_record(context)

        if args.write:
            # 正解ファイルを生成する
            if self.write_answer_file(file, record):
                self.exit_code = 0

        elif args.regression:
            # リグレッションテスト
            answer = self.read_answer_file(file)
            if self.test_regression(record, answer):
                self.exit_code = 0

        else:
            args.stdout = True
            self.exit_code = 0

        if args.stdout:
            # 標準出力に表示
            pprint.pprint(record)

        self.exit_code = 0 if (matched and analyzed) else 1

if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument('--auto', action='store_true')
    parser.add_argument('--write', action='store_true')
    parser.add_argument('--regression', action='store_true')
    parser.add_argument('--stdout', action='store_true')
    parser.add_argument('file')

    args = parser.parse_args()

    sys.exit(TestResultDetail(args.file).exit_code)
