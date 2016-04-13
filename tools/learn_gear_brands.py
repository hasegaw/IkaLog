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

from ikalog.utils import GearBrandRecoginizer
from ikalog import constants

sys.path.append('.')
train_basedir = sys.argv[1]



def learnImageGroup(recoginizer=None, name="unknown", dir=None):
    assert dir is not None
    assert recoginizer is not None

    train_dir = "%s/%s" % (train_basedir, dir)
    print("%s => %s" % (name, train_dir))
    recoginizer.learn_image_group(name=name, dir=train_dir)


def loopbackTest(recoginizer):
    results = {}
    misses = []
    total = 0
    correct = 0

    sort_zumi = {}

    for gearpower in recoginizer.groups:
        for sample_tuple in gearpower['images']:
            sample = sample_tuple[0]
            answer, distance = recoginizer.match(sample)  # = img

            total = total + 1
            if (gearpower['name'] == answer):
                correct = correct + 1
                msg = "正解"
            else:
                msg = "　 "
                misses.append(sample)

            if not answer in sort_zumi:
                sort_zumi[answer] = []
            sort_zumi[answer].append((distance, sample_tuple[3]))

            #print("%s: %s 結果: %s<br>" % (msg, gearpower['name'], r['name']))

    s = ("%d 問中 %d 問正解　　学習内容に対する正答率 %3.1f％" %
         (total, correct, correct / total * 100))

    # miss list 表示
    misses_hist = []
    for sample in misses:
        param, r = recoginizer.analyze_image(sample, debug=True)
        misses_hist.append(r)
    recoginizer.show_learned_icon_image(misses_hist, 'Misses', save='misses.png')

    # file にリスト書き出し
    f = open('recoginizer.html', 'w')
    f.write('<p>%s</p>' % s)
    for gearpower in sorted(sort_zumi.keys()):
        f.write('<h3>%s</h3>' % gearpower)
        print('<h3>%s</h3>' % gearpower)
        for t in sorted(sort_zumi[gearpower]):
            f.write('<font size=-4>%s</font><img src=%s alt="%s">' %
                    (t[0], t[1], t[0]))
            print('<font size=-4>%s</font><img src=%s alt="%s">' %
                  (t[0], t[1], t[0]))

    f.close()
    return s

gear_brands = GearBrandRecoginizer()

for brand in constants.gear_brands:
    learnImageGroup(gear_brands, brand, brand)

gear_brands.knn_train_from_group()
gear_brands.save_model_to_file()
gear_brands.knn_reset()
gear_brands.load_model_from_file()
gear_brands.knn_train()
if 1:
    s = loopbackTest(gear_brands)
    print(s)
