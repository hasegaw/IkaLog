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

import os
import sys

import ikalog.constants as constants
from ikalog.utils.icon_recoginizer import GearRecoginizer



def learnImageGroup(recoginizer, name, dir, train_basedir):
    if dir is None:
        return None

    train_dir = os.path.join(train_basedir, dir)
    print("%s => %s" % (name, train_dir))
    recoginizer.learn_image_group(name=name, dir=train_dir)

def check_train_accuracy(recoginizer):
    results = {}
    misses = []
    total = 0
    correct = 0

    sort_zumi = {}

    for group in recoginizer.groups:
        for sample in group['images']:
            print(sample['img'])
            answer, distance = recoginizer.predict(sample['img'])

            total = total + 1
            if (group['name'] == answer):
                correct = correct + 1
                msg = "正解"
            else:
                msg = "　 "
                misses.append(sample)

            if not answer in sort_zumi:
                sort_zumi[answer] = []
            sort_zumi[answer].append((distance, sample['src_path']))

    s = ("%d 問中 %d 問正解　　学習内容に対する正答率 %3.1f％" %
         (total, correct, correct / total * 100))

    # file にリスト書き出し
    f = open('gears.html', 'w')
    f.write('<p>%s</p>' % s)
    for gear in sorted(sort_zumi.keys()):
        f.write('<h3>%s</h3>' % gear)
        print('<h3>%s</h3>' % gear)
        for t in sorted(sort_zumi[gear]):
            f.write('<font size=-4>%s</font><img src="%s" alt="%s">' %
                    (t[0], t[1], t[0]))
            print('<font size=-4>%s</font><img src="%s" alt="%s">' %
                  (t[0], t[1], t[0]))

    f.close()
    return s


def train_type(classifier, gear_type, train_basedir):
    full_list = list({
        'weapon': constants.weapons,
        'headgear': constants.gear_headgear,
        'clothing': constants.gear_clothing,
        'shoes': constants.gear_shoes,
    }[gear_type].keys())

    basedir = os.path.join(train_basedir, gear_type)

    for gear_id in full_list:
        if os.path.exists(os.path.join(basedir, gear_id)):
            learnImageGroup(classifier, name=gear_id, dir=gear_id, train_basedir=basedir)
        else:
            print('missing: %s' % gear_id)

    classifier.knn_train_from_group()
    classifier.save_model_to_file()
    classifier.knn_reset()
    classifier.load_model_from_file()
    classifier.knn_train()
    if 1:
        s = check_train_accuracy(classifier)
        print(s)


if __name__ == "__main__":
    train_basedir = sys.argv[1]

    gear_head = GearRecoginizer('data/gears_head.knn.data')
    gear_clothing = GearRecoginizer('data/gears_clothing.knn.data')
    gear_shoes = GearRecoginizer('data/gears_shoes.knn.data')
    gear_weapon = GearRecoginizer('data/gears_weapon.knn.data')

    train_type(gear_weapon, 'weapon', train_basedir)
    train_type(gear_head, 'headgear', train_basedir)
    train_type(gear_clothing, 'clothing', train_basedir)
    train_type(gear_shoes, 'shoes', train_basedir)
    sys.exit()
