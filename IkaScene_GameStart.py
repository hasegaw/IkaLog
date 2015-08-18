#!python3
# -*- coding: utf-8 -*-
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

	modename_left = 640 - 300
	modename_right = 640 + 300
	modename_width = modename_right - modename_left
	modename_top = 250
	modename_bottom = 310
	modename_height = modename_bottom - modename_top

	def load_mapname_mask(self, frame, map_name):
		if frame is None:
			print("%s のマスクデータが読み込めませんでした。" % map_name)

		img_map = IkaUtils.cropImageGray(frame, self.mapname_left, self.mapname_top, self.mapname_width, self.mapname_height)

		keys = [ 'name', 'mask' ]
		values = [ map_name, img_map ]
		return dict(zip(keys, values))

	def load_modename_mask(self, frame, mode_name):
		if frame is None:
			print("%s のマスクデータが読み込めませんでした。" % mode_name)

		img_mode = IkaUtils.cropImageGray(frame, self.modename_left, self.modename_top, self.modename_width, self.modename_height)

		keys = [ 'name', 'mask' ]
		values = [ mode_name, img_mode ]
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

		self.map_list = []
		self.map_list.append(self.load_mapname_mask(data1, 'タチウオパーキング'))
		self.map_list.append(self.load_mapname_mask(data2, 'モズク農場'))
		self.map_list.append(self.load_mapname_mask(data3, 'ネギトロ炭鉱'))
		self.map_list.append(self.load_mapname_mask(data4, 'アロワナモール'))
		self.map_list.append(self.load_mapname_mask(data5, 'デカライン高架下'))
		self.map_list.append(self.load_mapname_mask(data6, 'Bバスパーク'))
		self.map_list.append(self.load_mapname_mask(data7, 'ハコフグ倉庫'))
		self.map_list.append(self.load_mapname_mask(data8, 'シオノメ油田'))
		self.map_list.append(self.load_mapname_mask(data9, 'モンガラキャンプ場'))
		self.map_list.append(self.load_mapname_mask(data10, 'ホッケ埠頭'))

		self.mode_list = []
		self.mode_list.append(self.load_modename_mask(data1, 'ガチエリア'))
		self.mode_list.append(self.load_modename_mask(data2, 'ナワバリバトル'))
		self.mode_list.append(self.load_modename_mask(data5, 'ガチヤグラ'))
		self.mode_list.append(self.load_modename_mask(data9, 'ガチホコバトル'))

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

	def guess_mode(self, frame):
		target_gray = IkaUtils.cropImageGray(frame, self.modename_left, self.modename_top, self.modename_width, self.modename_height)
		ret, src = cv2.threshold(target_gray, 230, 255, cv2.THRESH_BINARY)

		# モード名を判断
		for mode in self.mode_list:
			mask = mode['mask']

			match = IkaUtils.matchWithMask(src, mask, 0.99, 0.80)
			if match:
				#print("モード名 %s : %f" % (mode['name'], match))
				return mode
		
		return None

	def match(self, frame):
		#if not self.last_frame is None:		

		map = self.guess_map(frame)
		mode = self.guess_mode(frame)

		if (map or mode):
			keys = [ 'map', 'mode' ]
			values = [ map, mode ]	
			return dict(zip(keys, values))

		return None

if __name__ == "__main__":
	print(sys.argv)
	target = cv2.imread(sys.argv[1])

	obj = IkaScene_GameStart()

	r = obj.match(target)
	map = r['map']
	mode = r['mode']

	#map = obj.guess_map(target)
	#mode = obj.guess_mode(target)

	print(map)
	print(mode)

	#cv2.imshow('Scene', target)
	#k = cv2.waitKey(3000) # 1msec待つ

	if (map and mode):
		s = "ゲーム画面検出。 マップ: %s モード: %s" % (map['name'], mode['name'])
		print(s)
