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

from ikalog.utils.gearpower_recoginizer import GearpowerRecoginizer


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

    for gearpower in gearpowers.groups:
        for sample_tuple in gearpower['images']:
            sample = sample_tuple[0]
            answer, distance = gearpowers.match(sample)  # = img

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
        param, r = gearpowers.analyze_image(sample, debug=True)
        misses_hist.append(r)
    gearpowers.show_learned_gearpower_image(misses_hist, 'Misses', save='misses.png')

    # file にリスト書き出し
    f = open('gearpowers.html', 'w')
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

gearpowers = GearpowerRecoginizer()

learnImageGroup(gearpowers, "ボム飛距離アップ", dir="bomb_range_up" )
learnImageGroup(gearpowers, "ボムサーチ", dir="bomb_sniffer")
learnImageGroup(gearpowers, "マーキングガード", dir="cold_blooded")
learnImageGroup(gearpowers, "カムバック", dir="comeback")
learnImageGroup(gearpowers, "攻撃力アップ", dir="damage_up")
learnImageGroup(gearpowers, "防御力アップ", dir="defense_up")
learnImageGroup(gearpowers, "空", dir="empty")
learnImageGroup(gearpowers, "うらみ", dir="haunt")
learnImageGroup(gearpowers, "インク回復力アップ", dir="ink_recovery_up")
learnImageGroup(gearpowers, "安全シューズ", dir="ink_resistence_up")
learnImageGroup(gearpowers, "インク効率アップ（メイン）", dir="ink_saver_main")
learnImageGroup(gearpowers, "インク効率アップ（サブ）", dir="ink_saver_sub")
learnImageGroup(gearpowers, "ラストスパート", dir="last-ditch_effort")
learnImageGroup(gearpowers, "未開放", dir="locked")
learnImageGroup(gearpowers, "イカニンジャ", dir="ninja_squid")
learnImageGroup(gearpowers, "スタートダッシュ", dir="opening_gambit")
learnImageGroup(gearpowers, "復活時間短縮", dir="quick_respawn")
learnImageGroup(gearpowers, "スーパージャンプ時間短縮", dir="quick_super_jump")
learnImageGroup(gearpowers, "スタートレーダー", dir="recon")
learnImageGroup(gearpowers, "ヒト移動速度アップ", dir="run_speed_up")
learnImageGroup(gearpowers, "スペシャル増加量アップ", dir="special_charge_up")
learnImageGroup(gearpowers, "スペシャル時間延長", dir="special_duration_up")
learnImageGroup(gearpowers, "スペシャル減少量ダウン", dir="special_saver")
learnImageGroup(gearpowers, "ステルスジャンプ", dir="stealth_jump")
learnImageGroup(gearpowers, "イカダッシュ速度アップ", dir="swim_speed_up")
learnImageGroup(gearpowers, "逆境", dir="tenacity")

gearpowers.knn_train_from_group()
gearpowers.save_model_to_file('data/gearpowers.knn.data')
gearpowers.knn_reset()
gearpowers.load_model_from_file('data/gearpowers.knn.data')
gearpowers.knn_train()
if 1:
    s = loopbackTest()
    print(s)

if __name__ == "__main__":
    from ikalog.scenes.result_gears import *
    from ikalog.utils import *
    import os
    result_gears = ResultGears(None)
    result_gears.gearpowers = gearpowers
    sort_zumi = {}
    for file in sys.argv[2:]:
        context = {
            'engine': {
                'frame': cv2.imread(file),
            },
            'game': {
                'map': {'name': 'ハコフグ倉庫', },
                'rule': {'name': 'ガチエリア'},
            },'scenes':{},
        }
        print('file ', file, context['engine']['frame'].shape)

        
        result_gears._analyze(context)
        srcname, ext = os.path.splitext(os.path.basename(file))

        for n in range(len(context['scenes']['result_gears']['gears'])):
            gear = context['scenes']['result_gears']['gears'][n]
            for field in gear:
                if field == 'img_name':
                    continue
                elif field.startswith('img_'):
                    img_dir = os.path.join(
                        'test_result', 'gearpowers', gear[field.replace('img_','')])
                    img_file = os.path.join(img_dir, '%s.%d.%s.png' % (srcname, n, field))
                    print(img_file)
                    try:
                        os.makedirs(img_dir)
                    except:
                        pass
                    IkaUtils.writeScreenshot(img_file, gear[field])
