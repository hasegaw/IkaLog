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

import numpy as np
import cv2
import time
import sys
from IkaUtils import *

class IkaScene_GameStart:

	# 720p サイズでの値
	mapname_width = 430
	mapname_left = 1280 - mapname_width
	mapname_top = 580
	mapname_height = 640 - mapname_top

	rulename_left = 640 - 300
	rulename_right = 640 + 300
	rulename_width = rulename_right - rulename_left
	rulename_top = 250
	rulename_bottom = 310
	rulename_height = rulename_bottom - rulename_top

	def load_mapname_mask(self, frame, map_name):
		if frame is None:
			print("%s のマスクデータが読み込めませんでした。" % map_name)

		img_map = IkaUtils.cropImageGray(frame, self.mapname_left, self.mapname_top, self.mapname_width, self.mapname_height)

		keys = [ 'name', 'mask' ]
		values = [ map_name, img_map ]
		return dict(zip(keys, values))

	def load_rulename_mask(self, frame, rule_name):
		if frame is None:
			print("%s のマスクデータが読み込めませんでした。" % rule_name)

		img_rule = IkaUtils.cropImageGray(frame, self.rulename_left, self.rulename_top, self.rulename_width, self.rulename_height)

		keys = [ 'name', 'mask' ]
		values = [ rule_name, img_rule ]
		return dict(zip(keys, values))

	def __init__(self):
		data1 = cv2.imread('masks/gachi_tachiuo.png',1)
		data2 = cv2.imread('masks/nawabari_mozuku.png',1)
		data3 = cv2.imread('masks/gachi_negitoro.png',1)
		data4 = cv2.imread('masks/nawabari_arowana.png',1)
		data5 = cv2.imread('masks/yagura_decaline.png',1)
		data6 = cv2.imread('masks/gachi_buspark.png',1)
		data7 = cv2.imread('masks/gachi_hakofugu.png',1)
		data8 = cv2.imread('masks/gachi_shionome.png',1)
		data9 = cv2.imread('masks/hoko_mongara.png',1)
		data10 = cv2.imread('masks/nawabari_hokke.png',1)
		data11 = cv2.imread('masks/nawabari_hirame.png',1)
		data12 = cv2.imread('masks/nawabari_masaba.png',1)

		self.map_list = []
		self.map_list.append(self.load_mapname_mask(data1, 'タチウオパーキング'))
		self.map_list.append(self.load_mapname_mask(data2, 'モズク農園'))
		self.map_list.append(self.load_mapname_mask(data3, 'ネギトロ炭鉱'))
		self.map_list.append(self.load_mapname_mask(data4, 'アロワナモール'))
		self.map_list.append(self.load_mapname_mask(data5, 'デカライン高架下'))
		self.map_list.append(self.load_mapname_mask(data6, 'Bバスパーク'))
		self.map_list.append(self.load_mapname_mask(data7, 'ハコフグ倉庫'))
		self.map_list.append(self.load_mapname_mask(data8, 'シオノメ油田'))
		self.map_list.append(self.load_mapname_mask(data9, 'モンガラキャンプ場'))
		self.map_list.append(self.load_mapname_mask(data10, 'ホッケふ頭'))
		self.map_list.append(self.load_mapname_mask(data11, 'ヒラメが丘団地'))
		self.map_list.append(self.load_mapname_mask(data12, 'マサバ海峡大橋'))

		self.rule_list = []
		self.rule_list.append(self.load_rulename_mask(data1, 'ガチエリア'))
		self.rule_list.append(self.load_rulename_mask(data2, 'ナワバリバトル'))
		self.rule_list.append(self.load_rulename_mask(data5, 'ガチヤグラ'))
		self.rule_list.append(self.load_rulename_mask(data9, 'ガチホコバトル'))

	def guess_map(self, frame):
		target_gray = IkaUtils.cropImageGray(frame, self.mapname_left, self.mapname_top, self.mapname_width, self.mapname_height)
		ret, src = cv2.threshold(target_gray, 230, 255, cv2.THRESH_BINARY)

		# マップ名を判断
		for map in self.map_list:
			mask = map['mask']

			match = IkaUtils.matchWithMask(src, mask, 0.99, 0.80)
			if match:
				#print("マップ名 %s : %f" % (map['name'], match))
				return map

		return None

	def guess_rule(self, frame):
		target_gray = IkaUtils.cropImageGray(frame, self.rulename_left, self.rulename_top, self.rulename_width, self.rulename_height)
		ret, src = cv2.threshold(target_gray, 230, 255, cv2.THRESH_BINARY)

		# モード名を判断
		for rule in self.rule_list:
			mask = rule['mask']

			match = IkaUtils.matchWithMask(src, mask, 0.99, 0.80)
			if match:
				#print("モード名 %s : %f" % (rule['name'], match))
				return rule
		
		return None

	def match(self, context):
		map = self.guess_map(context['engine']['frame'])
		rule = self.guess_rule(context['engine']['frame'])

		if not map is None:
			context['game']['map'] = map
		if not rule is None:
			context['game']['rule'] = rule

		return (map or rule)

if __name__ == "__main__":
	print(sys.argv)
	target = cv2.imread(sys.argv[1])

	obj = IkaScene_GameStart()

	r = obj.match(target)
	map = r['map']
	rule = r['rule']

	#map = obj.guess_map(target)
	#rule = obj.guess_rule(target)

	print(map)
	print(rule)

	#cv2.imshow('Scene', target)
	#k = cv2.waitKey(3000) # 1msec待つ

	if (map and rule):
		s = "ゲーム画面検出。 マップ: %s モード: %s" % (map['name'], rule['name'])
		print(s)
