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

import cv2
from ikalog.utils import *


class Scene(object):

    # シーンクラスを単体で動作させるためのクラスメソッド
    @classmethod
    def main_func(cls):
        import traceback
        import sys

        files = sys.argv[1:]
        for f in files:
            context = {
                'engine': {'frame': cv2.imread(f), 'msec': 1000 * 60},
                'game': {}, 'lobby': {}, 'scenes': {},
                'file': f,
            }

            obj = cls(None)
            try:
                obj.match(context)
            except:
                IkaUtils.dprint('%s: Raised an exception:' % obj)
                IkaUtils.dprint(traceback.format_exc())

            try:
                obj.analyze(context)
            except:
                IkaUtils.dprint('%s: Raised an exception:' % obj)
                IkaUtils.dprint(traceback.format_exc())

            obj.dump(context)

    # 何らかの原因で Engine 全体がリセットした
    def reset(self):
        self._matched = None
        self._analyzed = None
        self._last_matched_msec = None

    # 新しいフレームの解析をはじめるときに呼ばれる
    def new_frame(self, context):
        self._matched = None

    # 現在のフレームにマッチしたときの処理
    def _set_matched(self, context):
        self._matched = True
        self._last_matched_msec = context['engine']['msec']

    def matched_in(self, context, duration_msec, attr='_last_matched_msec'):
        last_matched_msec = getattr(self, attr)
        if last_matched_msec is None:
            return False

        msec = context['engine']['msec']
        return (msec - duration_msec) < last_matched_msec

    def _analyze(self, context):
        raise Exception('%s: _analyze() must be overrided' % self)

    def analyze(self, context):
        analyzed = self._analyze(context)
        return analyzed

    def match_no_cache(self, context):
        raise Exception('%s: _match_no_cache must be overrided' % self)

    def match(self, context):
        if (self._matched is None):
            self._matched = self.match_no_cache(context)

            if self._matched:
                self._set_matched(context)

        return self._matched

    def _init_scene(self):
        pass

    def _call_plugins_nop(self, event_name):
        IkaUtils.dprint('%s: Tried to call plugin hook %s'
                        % (self, event_name))

    def is_another_scene_matched(self, context, scene_name):
        scene = self.find_scene_object(scene_name)

        return (scene is not None) and (scene.match(context) != False)

    def find_scene_object(self, scene_name):
        if (self.engine is None):
            return None

        if not (hasattr(self.engine, 'find_scene_object')):
            return None

        return self.engine.find_scene_object(scene_name)

    def dump(self, context):
        print(context['file'])
        print('matched %s' % self._matched)
        print('')

    def __init__(self, engine, debug=False):
        self.engine = engine
        self.exclusive_scene = False

        if (engine is not None) and hasattr(engine, 'call_plugins'):
            self._call_plugins = engine.call_plugins
        else:
            self._call_plugins = self._call_plugins_nop
        self._init_scene()

        self.reset()
