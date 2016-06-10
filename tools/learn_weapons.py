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

sys.path.append('.')
train_basedir = sys.argv[1]

import ikalog.constants as constants
from ikalog.utils import WeaponRecoginizer


def learnImageGroup(recoginizer=None, name="unknown", dir=None):
    if dir is None or recoginizer is None:
        return None

    train_dir = "%s/%s" % (train_basedir, dir)
    print("%s => %s" % (name, train_dir))
    recoginizer.learn_image_group(name=name, dir=train_dir)


def loopbackTest():
    results = {}
    misses = []
    total = 0
    correct = 0

    sort_zumi = {}

    for weapon in weapons.groups:
        for sample in weapon['images']:
            answer, distance = weapons.predict(sample['img'])

            total = total + 1
            if (weapon['name'] == answer):
                correct = correct + 1
                msg = "正解"
            else:
                msg = "　 "
                misses.append(sample)

            if not answer in sort_zumi:
                sort_zumi[answer] = []
            sort_zumi[answer].append((distance, sample['src_path']))

            #print("%s: %s 結果: %s<br>" % (msg, weapon['name'], r['name']))

    s = ("%d 問中 %d 問正解　　学習内容に対する正答率 %3.1f％" %
         (total, correct, correct / total * 100))

    # miss list 表示
    misses_hist = []
    for sample in []:  # misses:
        param, r = weapons.analyze_image(sample, debug=True)
        misses_hist.append(r)
    weapons.show_learned_icon_image(misses_hist, 'Misses', save='misses.png')

    # file にリスト書き出し
    f = open('weapons.html', 'w')
    f.write('<p>%s</p>' % s)
    for weapon in sorted(sort_zumi.keys()):
        f.write('<h3>%s</h3>' % weapon)
        print('<h3>%s</h3>' % weapon)
        for t in sorted(sort_zumi[weapon]):
            f.write('<font size=-4>%s</font><img src=%s alt="%s">' %
                    (t[0], t[1], t[0]))
            print('<font size=-4>%s</font><img src=%s alt="%s">' %
                  (t[0], t[1], t[0]))

    f.close()
    return s

weapons = WeaponRecoginizer()

for key in constants.weapons.keys():
    learnImageGroup(weapons, key, dir=key)

weapons.knn_train_from_group()
weapons.save_model_to_file()
weapons.knn_reset()
weapons.load_model_from_file()
weapons.knn_train()
if 1:
    s = loopbackTest()
    print(s)
    sys.exit()
