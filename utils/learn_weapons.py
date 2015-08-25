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
import sys
import numpy as np
import os

sys.path.append('.')

from IkaGlyphRecoginizer import *

weapons = IkaGlyphRecoginizer()

weapons.learnImageGroup(name = "L3リールガン", dir = "weapons/L3リールガン")
weapons.learnImageGroup(name = "N-ZAP85", dir = "weapons/NZAP85")
weapons.learnImageGroup(name = "N-ZAP89", dir = "weapons/オレンジ鉄砲")
weapons.learnImageGroup(name = "カーボンローラー", dir = "weapons/カーボンローラー")
weapons.learnImageGroup(name = "ガロン52", dir = "weapons/ガロン52")
weapons.learnImageGroup(name = "ガロン96", dir = "weapons/ガロン96")
weapons.learnImageGroup(name = "ガロンデコ52", dir = "weapons/ガロンデコ52")
weapons.learnImageGroup(name = "ガロンデコ96", dir = "weapons/ガロンデコ96")
weapons.learnImageGroup(name = "ジェットスイーパー", dir = "weapons/ジェットスイーパー")
weapons.learnImageGroup(name = "ジェットスイーパーカスタム", dir = "weapons/ジェットスイーパーカスタム")
weapons.learnImageGroup(name = "シャープマーカー", dir = "weapons/シャープマーカー")
weapons.learnImageGroup(name = "シャープマーカーネオ", dir = "weapons/シャープマーカーネオ")
weapons.learnImageGroup(name = "スイックリンα", dir = "weapons/スイックリンA")
weapons.learnImageGroup(name = "スプラシューター", dir = "weapons/スプラシューター")
weapons.learnImageGroup(name = "スプラシューターコラボ", dir = "weapons/スプラシューターコラボ")
weapons.learnImageGroup(name = "スプラスコープ", dir = "weapons/スプラスコープ")
weapons.learnImageGroup(name = "スプラスコープワカメ", dir = "weapons/スプラスコープワカメ")
weapons.learnImageGroup(name = "スプラチャージャー", dir = "weapons/スプラチャージャー")
weapons.learnImageGroup(name = "スプラチャージャーワカメ", dir = "weapons/スプラチャージャーワカメ")
weapons.learnImageGroup(name = "スプラローラー", dir = "weapons/スプラローラー")
weapons.learnImageGroup(name = "スプラローラーコラボ", dir = "weapons/スプラローラーコラボ")
weapons.learnImageGroup(name = "ダイナモローラー", dir = "weapons/ダイナモローラー")
weapons.learnImageGroup(name = "ダイナモローラーテスラ", dir = "weapons/ダイナモローラーテスラ")
weapons.learnImageGroup(name = "デュアルスイーパー", dir = "weapons/デュアルスイーパー無印")
weapons.learnImageGroup(name = "デュアルスイーパーカスタム", dir = "weapons/デュアルスイーパーカスタム")
weapons.learnImageGroup(name = "ノヴァブラスター", dir = "weapons/ノヴァブラスター")
weapons.learnImageGroup(name = "バケットスローシャー", dir = "weapons/バケットスローシャー")
weapons.learnImageGroup(name = "パブロ", dir = "weapons/パブロ")
weapons.learnImageGroup(name = "ヒーローシューターレプリカ", dir = "weapons/ヒーローシューターレプリカ")
weapons.learnImageGroup(name = "ヒーローローラーレプリカ", dir = "weapons/ヒーローローラーレプリカ")
weapons.learnImageGroup(name = "プライムシューター", dir = "weapons/プライムシューター")
weapons.learnImageGroup(name = "プライムシューターコラボ", dir = "weapons/プライムシューターコラボ")
weapons.learnImageGroup(name = "プロモデラーMG", dir = "weapons/プロモデラーMG銀")
weapons.learnImageGroup(name = "プロモデラーRG", dir = "weapons/プロモデラーRG金")
weapons.learnImageGroup(name = "ホットブラスター", dir = "weapons/ホットブラスター")
weapons.learnImageGroup(name = "ホットブラスターカスタム", dir = "weapons/ホットブラスターカスタム")
weapons.learnImageGroup(name = "リッター3k", dir = "weapons/リッター3k")
weapons.learnImageGroup(name = "リッター3kカスタム", dir = "weapons/リッター3kカスタム")
weapons.learnImageGroup(name = "ロングブラスター", dir = "weapons/ロングブラスター")
weapons.learnImageGroup(name = "ボールドマーカー", dir = "weapons/ボールドマーカー")
weapons.learnImageGroup(name = "ホクサイ", dir = "weapons/ホクサイ")
weapons.learnImageGroup(name = "もみじシューター", dir = "weapons/もみじシューター")
weapons.learnImageGroup(name = "わかばシューター", dir = "weapons/wakaba")

def loopbackTest():
	results = {}
	misses = []
	total = 0
	correct = 0

	for weapon in weapons.models:
		for sample in weapon['samples']:
			r, model = weapons.guessImage(sample)

			total = total + 1
			if (weapon['name'] == r['name']):
				correct = correct + 1
				msg = "正解"
			else:
				msg = "　 "
				misses.append(sample)

			#print("%s: %s 結果: %s<br>" % (msg, weapon['name'], r['name']))

	s = ("ループバック正答率 %3.1f％" % (correct / total * 100))

	# miss list 表示
	misses_hist = []
	for sample in misses:
		param, r = weapons.analyzeImage(sample, debug = True)
		misses_hist.append(r)
	weapons.showLearnedWeaponImage(misses_hist, 'Misses', save = 'misses.png')
	return s



#import timeit
#print(timeit.timeit('loopbackTest()', number=1, setup="from __main__ import loopbackTest,guessImage,guessImage1,weapons"))
s = loopbackTest()
#cv2.waitKey()
#sys.exit()

weapons.saveModelToFile("wepaons.trained")
weapons = None

# 他のファイルに対するテスト

