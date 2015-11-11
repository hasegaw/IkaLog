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

from ikalog.utils import IkaGlyphRecoginizer


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
        for sample_tuple in weapon['images']:
            sample = sample_tuple[0]
            answer, distance = weapons.match(sample)  # = img

            total = total + 1
            if (weapon['name'] == answer):
                correct = correct + 1
                msg = "正解"
            else:
                msg = "　 "
                misses.append(sample)

            if not answer in sort_zumi:
                sort_zumi[answer] = []
            sort_zumi[answer].append((distance, sample_tuple[3]))

            #print("%s: %s 結果: %s<br>" % (msg, weapon['name'], r['name']))

    s = ("%d 問中 %d 問正解　　学習内容に対する正答率 %3.1f％" %
         (total, correct, correct / total * 100))

    # miss list 表示
    misses_hist = []
    for sample in misses:
        param, r = weapons.analyze_image(sample, debug=True)
        misses_hist.append(r)
    weapons.show_learned_weapon_image(misses_hist, 'Misses', save='misses.png')

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

weapons = IkaGlyphRecoginizer()

learnImageGroup(weapons, "14式竹筒銃・甲", dir="14式竹筒銃・甲")
learnImageGroup(weapons, "3Kスコープ", dir="3Kスコープ")
learnImageGroup(weapons, "3Kスコープカスタム", dir="3Kスコープカスタム")
learnImageGroup(weapons, "L3リールガン", dir="L3リールガン")
learnImageGroup(weapons, "L3リールガンD", dir="L3リールガンD")
learnImageGroup(weapons, "H3リールガン", dir="H3リールガン")
learnImageGroup(weapons, "H3リールガンD", dir="H3リールガンD")
learnImageGroup(weapons, "N-ZAP85", dir="N-ZAP85")
learnImageGroup(weapons, "N-ZAP89", dir="N-ZAP89")
learnImageGroup(weapons, "オクタシューターレプリカ", dir="オクタシューター")
learnImageGroup(weapons, "カーボンローラー", dir="カーボンローラー")
learnImageGroup(weapons, "カーボンローラーデコ", dir="カーボンローラーデコ")
learnImageGroup(weapons, "ガロン52", dir="ガロン52")
learnImageGroup(weapons, "ガロン96", dir="ガロン96")
learnImageGroup(weapons, "ガロンデコ52", dir="ガロンデコ52")
learnImageGroup(weapons, "ガロンデコ96", dir="ガロンデコ96")
learnImageGroup(weapons, "ジェットスイーパー", dir="ジェットスイーパー")
learnImageGroup(weapons, "ジェットスイーパーカスタム", dir="ジェットスイーパーカスタム")
learnImageGroup(weapons, "シャープマーカー", dir="シャープマーカー")
learnImageGroup(weapons, "シャープマーカーネオ", dir="シャープマーカーネオ")
learnImageGroup(weapons, "スクイックリンα", dir="スクイックリンA")
learnImageGroup(weapons, "スクイックリンβ", dir="スクイックリンB")
learnImageGroup(weapons, "スプラシューター", dir="スプラシューター")
learnImageGroup(weapons, "スプラシューターコラボ", dir="スプラシューターコラボ")
learnImageGroup(weapons, "スプラスコープ", dir="スプラスコープ")
learnImageGroup(weapons, "スプラスコープワカメ", dir="スプラスコープワカメ")
learnImageGroup(weapons, "スプラスピナー", dir="スプラスピナー")
learnImageGroup(weapons, "スプラチャージャー", dir="スプラチャージャー")
learnImageGroup(weapons, "スプラチャージャーワカメ", dir="スプラチャージャーワカメ")
learnImageGroup(weapons, "スプラローラー", dir="スプラローラー")
learnImageGroup(weapons, "スプラローラーコラボ", dir="スプラローラーコラボ")
learnImageGroup(weapons, "ダイナモローラー", dir="ダイナモローラー")
learnImageGroup(weapons, "ダイナモローラーテスラ", dir="ダイナモローラーテスラ")
learnImageGroup(weapons, "デュアルスイーパー", dir="デュアルスイーパー無印")
learnImageGroup(weapons, "デュアルスイーパーカスタム", dir="デュアルスイーパーカスタム")
learnImageGroup(weapons, "ノヴァブラスター", dir="ノヴァブラスター")
learnImageGroup(weapons, "ノヴァブラスターネオ", dir="ノヴァブラスターネオ")
learnImageGroup(weapons, "バケットスローシャー", dir="バケットスローシャー")
learnImageGroup(weapons, "パブロ", dir="パブロ")
learnImageGroup(weapons, "パブロ・ヒュー", dir="パブロ・ヒュー")
learnImageGroup(weapons, "バレルスピナー", dir="バレルスピナー")
learnImageGroup(weapons, "バレルスピナーデコ", dir="バレルスピナーデコ")
learnImageGroup(weapons, "ヒーローシューターレプリカ", dir="ヒーローシューターレプリカ")
learnImageGroup(weapons, "ヒーローチャージャーレプリカ", dir="ヒーローチャージャーレプリカ")
learnImageGroup(weapons, "ヒーローローラーレプリカ", dir="ヒーローローラーレプリカ")
learnImageGroup(weapons, "ヒッセン", dir="ヒッセン")
learnImageGroup(weapons, "プライムシューター", dir="プライムシューター")
learnImageGroup(weapons, "プライムシューターコラボ", dir="プライムシューターコラボ")
learnImageGroup(weapons, "プロモデラーMG", dir="プロモデラーMG銀")
learnImageGroup(weapons, "プロモデラーRG", dir="プロモデラーRG金")
learnImageGroup(weapons, "ボールドマーカー", dir="ボールドマーカー")
learnImageGroup(weapons, "ホクサイ", dir="ホクサイ")
learnImageGroup(weapons, "ホットブラスター", dir="ホットブラスター")
learnImageGroup(weapons, "ホットブラスターカスタム", dir="ホットブラスターカスタム")
learnImageGroup(weapons, "もみじシューター", dir="もみじシューター")
learnImageGroup(weapons, "ラピッドブラスター", dir="ラピッドブラスター")
learnImageGroup(weapons, "Rブラスターエリート", dir="Rブラスターエリート")
learnImageGroup(weapons, "ラピッドブラスターデコ", dir="ラピッドブラスターデコ")
learnImageGroup(weapons, "リッター3K", dir="リッター3K")
learnImageGroup(weapons, "リッター3Kカスタム", dir="リッター3Kカスタム")
learnImageGroup(weapons, "ロングブラスター", dir="ロングブラスター")
learnImageGroup(weapons, "ロングブラスターカスタム", dir="ロングブラスターカスタム")
learnImageGroup(weapons, "わかばシューター", dir="わかばシューター")

weapons.knn_train_from_group()
weapons.save_model_to_file('data/weapons.knn.data')
weapons.knn_reset()
weapons.load_model_from_file('data/weapons.knn.data')
weapons.knn_train()
if 1:
    s = loopbackTest()
    print(s)

if __name__ == "__main__":
    from ikalog.scenes.result_detail import *
    from ikalog.utils import *
    result_detail = ResultDetail()
    result_detail.weapons = weapons
    sort_zumi = {}
    for file in sys.argv[2:]:
        context = {
            'engine': {
                'frame': cv2.imread(file),
            },
            'game': {
                'map': {'name': 'ハコフグ倉庫', },
                'rule': {'name': 'ガチエリア'},
            },
        }
        print('file ', file, context['engine']['frame'].shape)

        # 各プレイヤーの状況を分析
        result_detail.analyze(context)
        srcname, ext = os.path.splitext(os.path.basename(file))

        for n in range(len(context['game']['players'])):
            player = context['game']['players'][n]
            if 'weapon' in player:
                img_dir = os.path.join(
                    'test_result', 'weapons', player['weapon'])
                img_file = os.path.join(img_dir, '%s.%d.png' % (srcname, n))
                print(img_file)
                try:
                    os.makedirs(img_dir)
                except:
                    pass
                cv2.imwrite(img_file, player['img_weapon'])
