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

# IkaLogを使ってビデオファイルをリネームする
#
# 使い方
#   python tools\IkaRename.py K:\hoge.mp4
#   ->  "K:\20150913_2330_タチウオパーキング_ガチエリア_win.mp4"
#       などにリネームされる

import time
from ikalog.inputs import CVCapture
from ikalog.engine import IkaEngine
from ikalog import outputs
from ikalog.utils import *

class IkaRename:

    def createMP4Filename(self, context):
        map = IkaUtils.map2text(context['game']['map'], unknown='マップ不明')
        rule = IkaUtils.rule2text(context['game']['rule'], unknown='ルール不明')
        won = IkaUtils.getWinLoseText(
            context['game']['won'], win_text='win', lose_text='lose')

        timestamp = time.localtime(os.stat(file).st_mtime)
        time_str = time.strftime("%Y%m%d_%H%M", timestamp)
        newname = '%s_%s_%s_%s.mp4' % (time_str, map, rule, won)

        return newname

    def onFrameReadFailed(self, context):
        print('%s: たぶんファイルの終端にたどり着きました' % self.file)
        # もういいので IkaEngine を止める
        self.engine.stop()

    def onGameIndividualResult(self, context):
        mp4_filename = self.createMP4Filename(context)
        destname = os.path.join(os.path.dirname(self.file), mp4_filename)

        print('%s: 新ファイル名 %s' % (self.file, destname))

        # 強制的にキャプチャを閉じて IkaEngine も止める
        self.engine.capture.cap.release()
        self.engine.capture.cap = None
        self.engine.stop()

        os.rename(self.file, destname)

    def __init__(self, file):
        self.file = file

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
        self.engine.run()

if __name__ == "__main__":
    for file in sys.argv[1:]:
        IkaRename(file)
