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

sys.path.append('.')

from ikalog.inputs import CVCapture
from ikalog.utils import *
from ikalog.engine import *
from ikalog import outputs


class IkaTestGameStart:

    # 正解ファイルを作成する
    def answer_filename(self, video_file, answer_type, context):
        #basename_fullpath, ext = os.path.splitext(video_file)
        basename_fullpath = video_file
        answer_fullpath = basename_fullpath + '.answer.' + answer_type
        return answer_fullpath

    # 正解ファイルを作成する
    def write_answer_file(self, video_file, context):
        answer_fullpath = self.answer_filename(
            video_file, 'GameStart', context)

        record = {
            'stage': IkaUtils.map2text(self.engine.context['game'][
                'map'], unknown='None'),
            'rule': IkaUtils.rule2text(self.engine.context['game'][
                'rule'], unknown='None'),
        }

        f = open(answer_fullpath, 'w')
        f.write(json.dumps(record, separators=(',', ':')) + '\n')
        f.close()

        IkaUtils.dprint('wrote answer file %s' % answer_fullpath)
        return True

    def read_answer_file(self, video_file):
        answer_fullpath = self.answer_filename(video_file, 'GameStart', None)

        f = open(answer_fullpath, 'r')
        record = json.load(f)
        f.close()
        return record

    def test_regression(self, context, answer):
        stage = IkaUtils.map2text(self.engine.context['game'][
            'map'], unknown='None')
        rule = IkaUtils.rule2text(self.engine.context['game'][
                                  'rule'], unknown='None')

        IkaUtils.dprint('  detected: stage %s rule %s' % (stage, rule))
        IkaUtils.dprint('  answer  : stage %s rule %s' %
                        (answer['stage'], answer['rule']))

        assert(stage == answer['stage'])
        assert(rule == answer['rule'])
        return True

    def on_frame_read(self, context):
        if (context['engine']['msec'] > 60 * 1000):
            IkaUtils.dprint('%s: プレイから60秒以内にマップが検出できませんでした' % self)
            self.engine.stop()

    def on_game_go_sign(self, context):
        IkaUtils.dprint('%s: ゴーサインがでました' % self)
        self.engine.stop()

    def on_frame_read_failed(self, context):
        IkaUtils.dprint('%s: たぶんファイルの終端にたどり着きました' % self)
        self.engine.stop()

    def on_game_start(self, context):
        IkaUtils.dprint('%s: ゲーム検出' % self)
        self.engine.stop()

    def __init__(self, file):
        # インプットとして指定されたファイルを読む
        source = CVCapture()
        source.start_recorded_file(file)
        source.need_resize = True

        # 画面が見えないと進捗が判らないので
        screen = outputs.Screen(0, size=(640, 360))

        # プラグインとして自分自身（画面）を設定しコールバックを受ける
        outputPlugins = [self, screen]

        # IkaEngine を実行
        self.engine = IkaEngine()
        self.engine.pause(False)
        self.engine.set_capture(source)
        self.engine.set_plugins(outputPlugins)
        try:
            self.engine.run()
        except:
            pass

        if args.write:
            # 正解ファイルを生成する
            if self.write_answer_file(file, self.engine.context):
                self.exit_code = 0

        elif args.regression:
            # リグレッションテスト
            answer = self.read_answer_file(file)
            if self.test_regression(self.engine.context, answer):
                self.exit_code = 0

        else:
            args.stdout = True
            self.exit_code = 0

        if args.stdout:
            # 標準出力に表示
            map = IkaUtils.map2text(self.engine.context['game'][
                                    'map'], unknown='None')
            rule = IkaUtils.rule2text(self.engine.context['game'][
                                      'rule'], unknown='None')
            print(file, map, rule)


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument('--auto', action='store_true')
    parser.add_argument('--write', action='store_true')
    parser.add_argument('--regression', action='store_true')
    parser.add_argument('--stdout', action='store_true')
    parser.add_argument('file')

    args = parser.parse_args()

    print(args.auto)
    print(args.write)
    print(args.file)

    sys.exit(IkaTestGameStart(args.file).exit_code)
