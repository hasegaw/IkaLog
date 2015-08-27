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
train_basedir = sys.argv[1]

from IkaGlyphRecoginizer import *

def learnImageGroup(recoginizer =  None, name = "unknown", dir = None):
	if dir is None or recoginizer is None:
		return None

	train_dir = "%s/%s" % (train_basedir, dir)
	print("%s => %s" % (name, train_dir))
	recoginizer.learnImageGroup(name = name, dir = train_dir)


weapons = IkaGlyphRecoginizer()

learnImageGroup(weapons, "3Kスコープ", dir = "3Kスコープ")
learnImageGroup(weapons, "L3リールガン", dir = "L3リールガン")
learnImageGroup(weapons, "N-ZAP85", dir = "NZAP85")
learnImageGroup(weapons, "N-ZAP89", dir = "オレンジ鉄砲")
learnImageGroup(weapons, "カーボンローラー", dir = "カーボンローラー")
learnImageGroup(weapons, "ガロン52", dir = "ガロン52")
learnImageGroup(weapons, "ガロン96", dir = "ガロン96")
learnImageGroup(weapons, "ガロンデコ52", dir = "ガロンデコ52")
learnImageGroup(weapons, "ガロンデコ96", dir = "ガロンデコ96")
learnImageGroup(weapons, "ジェットスイーパー", dir = "ジェットスイーパー")
learnImageGroup(weapons, "ジェットスイーパーカスタム", dir = "ジェットスイーパーカスタム")
learnImageGroup(weapons, "シャープマーカー", dir = "シャープマーカー")
learnImageGroup(weapons, "シャープマーカーネオ", dir = "シャープマーカーネオ")
learnImageGroup(weapons, "スイックリンα", dir = "スイックリンA")
learnImageGroup(weapons, "スイックリンβ", dir = "スイックリンB")
learnImageGroup(weapons, "スプラシューター", dir = "スプラシューター")
learnImageGroup(weapons, "スプラシューターコラボ", dir = "スプラシューターコラボ")
learnImageGroup(weapons, "スプラスコープ", dir = "スプラスコープ")
learnImageGroup(weapons, "スプラスコープワカメ", dir = "スプラスコープワカメ")
learnImageGroup(weapons, "スプラチャージャー", dir = "スプラチャージャー")
learnImageGroup(weapons, "スプラチャージャーワカメ", dir = "スプラチャージャーワカメ")
learnImageGroup(weapons, "スプラローラー", dir = "スプラローラー")
learnImageGroup(weapons, "スプラローラーコラボ", dir = "スプラローラーコラボ")
learnImageGroup(weapons, "ダイナモローラー", dir = "ダイナモローラー")
learnImageGroup(weapons, "ダイナモローラーテスラ", dir = "ダイナモローラーテスラ")
learnImageGroup(weapons, "デュアルスイーパー", dir = "デュアルスイーパー無印")
learnImageGroup(weapons, "デュアルスイーパーカスタム", dir = "デュアルスイーパーカスタム")
learnImageGroup(weapons, "ノヴァブラスター", dir = "ノヴァブラスター")
learnImageGroup(weapons, "バケットスローシャー", dir = "バケットスローシャー")
learnImageGroup(weapons, "パブロ", dir = "パブロ")
learnImageGroup(weapons, "パブロ・ヒュー", dir = "パブロ・ヒュー")
learnImageGroup(weapons, "ヒーローシューターレプリカ", dir = "ヒーローシューターレプリカ")
learnImageGroup(weapons, "ヒーローチャージャーレプリカ", dir = "ヒーローチャージャーレプリカ")
learnImageGroup(weapons, "ヒーローローラーレプリカ", dir = "ヒーローローラーレプリカ")
learnImageGroup(weapons, "プライムシューター", dir = "プライムシューター")
learnImageGroup(weapons, "プライムシューターコラボ", dir = "プライムシューターコラボ")
learnImageGroup(weapons, "プロモデラーMG", dir = "プロモデラーMG銀")
learnImageGroup(weapons, "プロモデラーRG", dir = "プロモデラーRG金")
learnImageGroup(weapons, "ホットブラスター", dir = "ホットブラスター")
learnImageGroup(weapons, "ホットブラスターカスタム", dir = "ホットブラスターカスタム")
learnImageGroup(weapons, "ラピッドブラスター", dir = "ラピッドブラスター")
learnImageGroup(weapons, "ラピッドブラスターデコ", dir = "ラピッドブラスターデコ")
learnImageGroup(weapons, "リッター3k", dir = "リッター3k")
learnImageGroup(weapons, "リッター3kカスタム", dir = "リッター3kカスタム")
learnImageGroup(weapons, "ロングブラスター", dir = "ロングブラスター")
learnImageGroup(weapons, "ボールドマーカー", dir = "ボールドマーカー")
learnImageGroup(weapons, "ホクサイ", dir = "ホクサイ")
learnImageGroup(weapons, "もみじシューター", dir = "もみじシューター")
learnImageGroup(weapons, "わかばシューター", dir = "wakaba")

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

	s = ("%d 問中 %d 問正解　　学習内容に対する正答率 %3.1f％" % (total, correct, correct / total * 100))

	# miss list 表示
	misses_hist = []
	for sample in misses:
		param, r = weapons.analyzeImage(sample, debug = True)
		misses_hist.append(r)
	weapons.showLearnedWeaponImage(misses_hist, 'Misses', save = 'misses.png')
	return s

def testModel():
	for weapon in weapons.models:
		weapons.testModel(weapon)

testModel()

#import timeit
#print(timeit.timeit('loopbackTest()', number=1, setup="from __main__ import loopbackTest,guessImage,guessImage1,weapons"))
print(loopbackTest())
#cv2.waitKey()
#sys.exit()

weapons.saveModelToFile("data/weapons.trained")
weapons = None
