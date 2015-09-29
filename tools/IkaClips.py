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

# IkaLogを各種シーンを自動的に抜き出す

import sys
import os
import pprint

sys.path.append('.')

from ikalog.inputs.cvcapture import *
from ikalog.engine import *
from ikalog.outputs.preview import *
from ikalog.utils import *


class IkaClips:

    def onGameStart(self, context):
        self.t_GameStart = context['engine']['msec']

    def onGameGoSign(self, context):
        start = context['engine'][
            'msec'] if not self.t_GameStart else self.t_GameStart

        clip = {
            'file': self.file,
            'type': 'GameStart',
            'start': start - 5 * 1000,
            'end': context['engine']['msec'] + 1 * 1000,
        }
        self.clips.append(clip)

    def onGameKilled(self, context):
        clip = {
            'file': self.file,
            'type': 'kill',
            'start': context['engine']['msec'] - 6 * 1000,
            'end': context['engine']['msec'] + 2.5 * 1000,
        }
        self.clips.append(clip)

    def onGameDead(self, context):
        clip = {
            'file': self.file,
            'type': 'death',
            'start': context['engine']['msec'] - 6 * 1000,
            'end': context['engine']['msec'] + 2.5 * 1000,
        }
        self.clips.append(clip)

    def onGameFinish(self, context):
        clip = {
            'file': self.file,
            'type': 'finish',
            'start': context['engine']['msec'] - 6 * 1000,
            'end': context['engine']['msec'] + 10 * 1000,
        }
        self.clips.append(clip)

    def onFrameReadFailed(self, context):
        self.engine.stop()

    def onGameIndividualResult(self, context):
        # 強制的にキャプチャを閉じて IkaEngine も止める
        self.engine.capture.cap.release()
        self.engine.capture.cap = None
        self.engine.stop()

    def merge(self):
        # クリップをマージ

        new_clips = []
        last_clip = None
        for clip in self.clips:
            if last_clip and last_clip['end'] < clip['start']:
                new_clips.append(last_clip)
                last_clip = None

            if last_clip is None:
                last_clip = clip
                continue

            if clip['start'] < last_clip['end']:
                last_clip['type'] = '%s+%s' % (last_clip['type'], clip['type'])
                last_clip['end'] = clip['end']

        if not last_clip is None:
            new_clips.append(last_clip)

        IkaUtils.dprint('%d clips are merged to %d clips.' %
                        (len(self.clips), len(new_clips)))

        self.clips = new_clips

    def analyze(self, file):
        self.file = file
        self.clips = []
        self.t_GameStart = None

        # インプットとして指定されたファイルを読む
        source = CVCapture()
        source.start_recorded_file(file)
        source.need_resize = True

        # 画面が見えないと進捗が判らないので
        screen = Screen(0, size=(640, 360))

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
            # print('IkaEngineが落ちたので分析終了です')

        IkaUtils.dprint('%d clips found.' % (len(self.clips)))

    _cut_number = 0

    def msec2time(self, msec):
        sec = int(msec / 100.0) / 10.0
        if (sec <= 0.0):
            return '00:00:00.0'

        hh = '{0:02d}'.format(int(sec / 3600))
        mm = '{0:02d}'.format(int(sec / 60) % 60)
        ss = '{0:02d}'.format(int(sec % 60))
        ms = int((sec - int(sec)) * 10)
        s = '%s:%s:%s.%s' % (hh, mm, ss, ms)
        return s

    def duration(self, msec1, msec2):
        duration = max(msec1, msec2) - min(msec1, msec2)
        duration = int(duration / 100.0) / 10.0
        return '%.1f' % duration

    def cutVideoFile1(self, clip):
        self._cut_number = self._cut_number + 1

        srcname, ext = os.path.splitext(os.path.basename(self.file))
        destfile = os.path.join(self.tmp_dir, '%s.%d.%s.avi' % (
            srcname, self._cut_number, clip['type']))

        at = self.msec2time(clip['start'])
        dur = self.duration(clip['start'], clip['end'])

        cmd = 'ffmpeg -y -i %s -ss %s -t %s -f avi -acodec copy -vcodec huffyuv %s' % (
            clip['file'], at, dur, destfile)
        IkaUtils.dprint(cmd)

        os.system(cmd)

        clip['file_out'] = destfile

    def cutVideoFile(self):
        IkaUtils.dprint('Cutting clips from original file...')
        for clip in self.clips:
            self.cutVideoFile1(clip)

    def concatenateClips(self):
        IkaUtils.dprint('Concatinating clips...')
        srcname, ext = os.path.splitext(os.path.basename(self.file))
        destfile = os.path.join(self.out_dir, srcname + '.summary.mp4')

        files = []
        for clip in self.clips:
            files.append(clip['file_out'])

        args_i = '-i "concat:%s|"' % ("|".join(files))

        cmd = 'ffmpeg -y %s -vf scale=640:360 -f mp4 -c:v libx264 -b:v 1M -c:a copy %s' % (
            args_i, destfile)
        IkaUtils.dprint(cmd)

        os.system(cmd)

        for clip in self.clips:
            os.remove(clip['file_out'])

    def __init__(self):
        self.scenes = []
        self.tmp_dir = '/tmp/'
        self.out_dir = './'

if __name__ == "__main__":
    for file in sys.argv[1:]:
        clips = IkaClips()
        clips.analyze(file)
        pprint.pprint(clips.clips)
        clips.merge()
        pprint.pprint(clips.clips)
        clips.cutVideoFile()
        clips.concatenateClips()
