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
import numpy as np

from ikalog.utils.character_recoginizer import *
from ikalog.utils import *
from ikalog.constants import weapons_v2


# TODO: handle additional cause of death defined in weapons_v2 dict.


def filename2id(filename, id_keys):
    # Accept these filename formats:
    # h3reelgun.[xxx.xxx.]png
    # h3reelgun[.xxx]/xxx.[xxx.]png

    dirname = os.path.basename(os.path.dirname(filename).split('.')[0])
    basename = os.path.basename(filename).split('.')[0]

    if dirname in id_keys:
        return dirname
    if basename in id_keys:
        return basename
    raise KeyError


class DeadlyWeaponRecoginizer(CharacterRecoginizer):

    def name2id(self, name):
        try:
            return self.name2id_table.index(name)
        except:
            self.name2id_table.append(name)
            return self.name2id_table.index(name)

    def id2name(self, id):
        return self.name2id_table[id]

    def _normalize(self, img):
        img_weapon_b = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
        # cv2.imshow('hoge', img)
        array0to1280 = np.array(range(1280), dtype=np.int32)
        img_chars = np.sum(img_weapon_b[:, :], axis=1)  # 行毎の検出dot数
        img_char_extract_y = np.extract(
            img_chars > 0, array0to1280[0:len(img_chars)])

        if len(img_char_extract_y) < 1:
            return None

        y1 = np.amin(img_char_extract_y)
        y2 = np.amax(img_char_extract_y) + 1

        if (y2 - y1) < 2:
            return None

        img_weapon_b = img_weapon_b[y1:y2, :]

        new_height = self.sample_height
        new_width = int(img_weapon_b.shape[
                        1] * (new_height / img_weapon_b.shape[0]))
        img_weapon_b32 = cv2.resize(img_weapon_b, (new_width, new_height))

        # 横方向を crop

        array0to1280 = np.array(range(1280), dtype=np.int32)
        img_chars = np.sum(img_weapon_b32[:, :], axis=0)
        img_char_extract_x = np.extract(
            img_chars > 0, array0to1280[0:len(img_chars)])

        if len(img_char_extract_x) < 1:
            return None

        x1 = np.amin(img_char_extract_x)
        x2 = np.amax(img_char_extract_x) + 1

        if (x2 - x1 > 160):
            x2 = x1 + 160
        img_weapon_final = np.zeros((new_height, new_height * 10), np.uint8)
        img_weapon_final[:, 0: x2 - x1] = img_weapon_b32[:, x1:x2]
        if False:
            cv2.imshow('deadly weapon', img_weapon_b32)
            cv2.imshow('deadly weapon_final', img_weapon_final)

        return img_weapon_final

    def match(self, img):
        try:
            img_normalized = self._normalize(img)
            r = super(DeadlyWeaponRecoginizer, self).match1(img_normalized)
        except:
            print(img.shape)
            return 'unknown'

        index = r - ord('0')
        try:
            return self.id2name(index)

        except IndexError:
            IkaUtils.dprint('%s: FIXME: match1() returned invalid index (%s)' % (self, index))
            IkaUtils.dprint('%s: id2name_table (len %d) == %s' % (self, len(self.name2id_table), self.name2id_table))
            return 'unknown'

    def _find_png_files(self, dir):
        list = []
        for root, dirs, files in os.walk(dir):
            for file in sorted(files):
                if file.endswith(".png"):
                    f = os.path.join(root, file)
                    list.append(f)
        return list

    # 保存項目追加のために save/load をオーバーライド
    def save_model_to_file(self, file):
        f = open(file, 'wb')
        pickle.dump([self.samples, self.responses, self.name2id_table], f)
        f.close()

    def load_model_from_file(self, file):
        f = open(file, 'rb')
        l = pickle.load(f)
        f.close()
        self.samples = l[0]
        self.responses = l[1]
        self.name2id_table = l[2]

    def __new__(cls, *args, **kwargs):

        if not hasattr(cls, '__instance__'):
            cls.__instance__ = super(
                DeadlyWeaponRecoginizer, cls).__new__(cls, *args, **kwargs)

        return cls.__instance__

    def __init__(self):
        if hasattr(self, 'trained') and self.trained:
            return

        super(DeadlyWeaponRecoginizer, self).__init__()

        self.name2id_table = []

        self.x_cutter = self  # 変則的だがカッターとして自分を使う
        self.sample_height = 16

        lang = Localization.get_game_languages()[0]
        for lang_ in Localization.get_game_languages():
            model_name = 'data/deadly_weapons.%s.model' % lang_
            if os.path.isfile(model_name):
                lang = lang_
                break

        model_name = 'data/deadly_weapons.%s.model' % lang

        if os.path.isfile(model_name):
            self.load_model_from_file(model_name)
            self.train()
            return


        for weapons_id in weapons_v2.keys():
            dirname = 'training/deadly_weapons/%s/%s.%s' %  (lang, weapons_id, weapons_v2[weapons_id]['name']['ja_JP'])
            if not os.path.exists(dirname):
                os.mkdir(dirname)

        samples_path = 'training/deadly_weapons/%s' % lang
        IkaUtils.dprint('Building %s from %s' % (model_name, samples_path))
        data = []

        for file in self._find_png_files(samples_path):
            weapon_name = None
            if os.path.splitext(file)[1] != '.png':
                continue
            try:
                weapon_name = filename2id(file, weapons_v2)
            except KeyError:
                print('KeyError %s' % file)

            img = cv2.imread(file)
            img_normalized = self._normalize(img)

            if img_normalized is None:
                continue

            # サンプル数が足りないので3回学習
            img_normalized = cv2.cvtColor(img_normalized, cv2.COLOR_GRAY2BGR)
            self.add_sample(self.name2id(weapon_name), img_normalized)

        IkaUtils.dprint('Writing %s' % model_name)
        self.save_model_to_file(model_name)

        self.train()

if __name__ == "__main__":
    import sys
    obj = DeadlyWeaponRecoginizer()

    # 引数で PNG ファイルを渡されている場合は、それに対して
    # 認識処理を行う

    last_class = None
    list = []
    for file in sys.argv[1:]:
        img = cv2.imread(file)
        if img is None:
            continue
        cv2.imshow('input', img)

        r = obj.match(img)

        t = (r, file)
        list.append(t)

    for t in sorted(list):
        if last_class != t[0]:
            last_class = t[0]
            print("<h3>%s</h3>" % last_class)
        print('<!-- %s --><img src=%s>' % (t[0], t[1]))
