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

learnImageGroup(weapons, "14式竹筒銃・甲", dir="14式竹筒銃・甲")
learnImageGroup(weapons, "14式竹筒銃・乙", dir="14式竹筒銃・乙")
learnImageGroup(weapons, "14式竹筒銃・丙", dir="14式竹筒銃・丙")
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
learnImageGroup(weapons, "スクイックリンγ", dir="スクイックリンG")
learnImageGroup(weapons, "スクリュースロッシャー", dir="スクリュースロッシャー")
learnImageGroup(weapons, "スクリュースロッシャーネオ", dir="スクリュースロッシャーネオ")
learnImageGroup(weapons, "スプラシューター", dir="スプラシューター")
learnImageGroup(weapons, "スプラシューターコラボ", dir="スプラシューターコラボ")
learnImageGroup(weapons, "スプラシューターワサビ", dir="スプラシューターワサビ")
learnImageGroup(weapons, "スプラスコープ", dir="スプラスコープ")
learnImageGroup(weapons, "スプラスコープワカメ", dir="スプラスコープワカメ")
learnImageGroup(weapons, "スプラスピナー", dir="スプラスピナー")
learnImageGroup(weapons, "スプラスピナーコラボ", dir="スプラスピナーコラボ")
learnImageGroup(weapons, "スプラスピナーリペア", dir="スプラスピナーリペア")
learnImageGroup(weapons, "スプラチャージャー", dir="スプラチャージャー")
learnImageGroup(weapons, "スプラチャージャーワカメ", dir="スプラチャージャーワカメ")
learnImageGroup(weapons, "スプラローラー", dir="スプラローラー")
learnImageGroup(weapons, "スプラローラーコラボ", dir="スプラローラーコラボ")
learnImageGroup(weapons, "ダイナモローラー", dir="ダイナモローラー")
learnImageGroup(weapons, "ダイナモローラーテスラ", dir="ダイナモローラーテスラ")
learnImageGroup(weapons, "ダイナモローラーバーンド", dir="ダイナモローラーバーンド")
learnImageGroup(weapons, "デュアルスイーパー", dir="デュアルスイーパー無印")
learnImageGroup(weapons, "デュアルスイーパーカスタム", dir="デュアルスイーパーカスタム")
learnImageGroup(weapons, "ノヴァブラスター", dir="ノヴァブラスター")
learnImageGroup(weapons, "ノヴァブラスターネオ", dir="ノヴァブラスターネオ")
learnImageGroup(weapons, "ハイドラント", dir="ハイドラント")
learnImageGroup(weapons, "ハイドラントカスタム", dir="ハイドラントカスタム")
learnImageGroup(weapons, "バケットスロッシャー", dir="バケットスロッシャー")
learnImageGroup(weapons, "バケットスロッシャーデコ", dir="バケットスロッシャーデコ")
learnImageGroup(weapons, "バケットスロッシャーソーダ", dir="バケットスロッシャーソーダ")
learnImageGroup(weapons, "パブロ", dir="パブロ")
learnImageGroup(weapons, "パブロ・ヒュー", dir="パブロ・ヒュー")
learnImageGroup(weapons, "パーマネント・パブロ", dir="パーマネント・パブロ")
learnImageGroup(weapons, "バレルスピナー", dir="バレルスピナー")
learnImageGroup(weapons, "バレルスピナーデコ", dir="バレルスピナーデコ")
learnImageGroup(weapons, "ヒーローシューターレプリカ", dir="ヒーローシューターレプリカ")
learnImageGroup(weapons, "ヒーローチャージャーレプリカ", dir="ヒーローチャージャーレプリカ")
learnImageGroup(weapons, "ヒーローローラーレプリカ", dir="ヒーローローラーレプリカ")
learnImageGroup(weapons, "ヒッセン", dir="ヒッセン")
learnImageGroup(weapons, "ヒッセン・ヒュー", dir="ヒッセン・ヒュー")
learnImageGroup(weapons, "プライムシューター", dir="プライムシューター")
learnImageGroup(weapons, "プライムシューターコラボ", dir="プライムシューターコラボ")
learnImageGroup(weapons, "プライムシューターベリー", dir="プライムシューターベリー")
learnImageGroup(weapons, "プロモデラーMG", dir="プロモデラーMG銀")
learnImageGroup(weapons, "プロモデラーRG", dir="プロモデラーRG金")
learnImageGroup(weapons, "ボールドマーカー", dir="ボールドマーカー")
learnImageGroup(weapons, "ボールドマーカーネオ", dir="ボールドマーカーネオ")
learnImageGroup(weapons, "ホクサイ", dir="ホクサイ")
learnImageGroup(weapons, "ホクサイ・ヒュー", dir="ホクサイ・ヒュー")
learnImageGroup(weapons, "ホットブラスター", dir="ホットブラスター")
learnImageGroup(weapons, "ホットブラスターカスタム", dir="ホットブラスターカスタム")
learnImageGroup(weapons, "もみじシューター", dir="もみじシューター")
learnImageGroup(weapons, "ラピッドブラスター", dir="ラピッドブラスター")
learnImageGroup(weapons, "Rブラスターエリート", dir="Rブラスターエリート")
learnImageGroup(weapons, "Rブラスターエリートデコ", dir="Rブラスターエリートデコ")
learnImageGroup(weapons, "ラピッドブラスターデコ", dir="ラピッドブラスターデコ")
learnImageGroup(weapons, "リッター3K", dir="リッター3K")
learnImageGroup(weapons, "リッター3Kカスタム", dir="リッター3Kカスタム")
learnImageGroup(weapons, "ロングブラスター", dir="ロングブラスター")
learnImageGroup(weapons, "ロングブラスターカスタム", dir="ロングブラスターカスタム")
learnImageGroup(weapons, "わかばシューター", dir="わかばシューター")

weapons.knn_train_from_group()
weapons.save_model_to_file()
weapons.knn_reset()
weapons.load_model_from_file()
weapons.knn_train()
if 1:
    s = loopbackTest()
    print(s)
    sys.exit()
