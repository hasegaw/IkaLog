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
import os

from ikalog.utils.character_recoginizer import *
from ikalog.utils import *


class FesGenderRecoginizer(CharacterRecoginizer):

    def __new__(cls, *args, **kwargs):

        if not hasattr(cls, '__instance__'):
            cls.__instance__ = super(
                FesGenderRecoginizer, cls).__new__(cls, *args, **kwargs)

        return cls.__instance__

    def _find_png_files(self, dir):
        list = []
        for root, dirs, files in os.walk(dir):
            for file in sorted(files):
                if file.endswith(".png"):
                    f = os.path.join(root, file)
                    list.append(f)
        return list

    def match(self, img):
        r = super(FesGenderRecoginizer, self).match(img)

        return {
            '0': {'ja': 'ボーイ', 'en': 'boy', },
            '1': {'ja': 'ガール', 'en': 'girl', },
        }[r]

    def __init__(self):
        if hasattr(self, 'trained') and self.trained:
            return

        super(FesGenderRecoginizer, self).__init__()

        # フェスの性別認識(日本語版)にあたって
        # - 横幅 36 ドット、高さ18ドットで処理する
        self.x_cutter = FixedWidth(36, from_right=True)
        self.sample_height = 18

        model_name = 'data/fes_gender.model'
        if os.path.isfile(model_name):
            self.load_model_from_file(model_name)
            self.train()
            return

        IkaUtils.dprint('Building fes_gender recoginization model.')
        data = []

        for file in self._find_png_files('fes/gender_boy'):
            data.append({'file': file, 'response': 0})
        for file in self._find_png_files('fes/gender_girl'):
            data.append({'file': file, 'response': 1})

        for d in data:
            d['img'] = cv2.imread(d['file'])[0: 18, :, :]
            # サンプル数が足りないので3回学習
            self.add_sample(d['response'], d['img'])
            self.add_sample(d['response'], d['img'])
            self.add_sample(d['response'], d['img'])

        self.save_model_to_file(model_name)

        self.train()

if __name__ == "__main__":
    import sys
    obj = FesGenderRecoginizer()

    # 引数で PNG ファイルを渡されている場合は、それに対して
    # 認識処理を行う

    list = []
    for file in sys.argv[1:]:
        img = cv2.imread(file)
        cv2.imshow('input', img)

        r = obj.match(img)

        t = (r['ja'], file)
        list.append(t)

    for t in sorted(list):
        print('<img src=%s>' % t[1])
