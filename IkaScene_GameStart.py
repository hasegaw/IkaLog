#!/usr/local/bin/python3
# -*- coding: utf-8 -*-
import numpy as np
import cv2
import time
import sys
import slackweb

class IkaScene_GameStart:

	# 720p サイズでの値
	mapname_width = 430
	mapname_top = 580
	mapname_height = 640 - mapname_top

	modename_left = 640 - 300
	modename_right = 640 + 300
	modename_top = 250
	modename_bottom = 310

	def load_mapname_mask(self, frame, map_name):
		gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
		img_map = gray[self.mapname_top : self.mapname_height + self.mapname_top, 1280 - self.mapname_width:1280]

		keys = [ 'name', 'mask' ]
		values = [ map_name, img_map ]
		return dict(zip(keys, values))

	def load_modename_mask(self, frame, mode_name):
		gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
		img_mode = gray[self.modename_top : self.modename_bottom, self.modename_left : self.modename_right]

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
		cropped = frame[self.mapname_top : self.mapname_height + self.mapname_top, 1280 - self.mapname_width:1280]
		target_gray = cv2.cvtColor(cropped, cv2.COLOR_BGR2GRAY)
		#cv2.imshow('Scene', target_gray)
		#k = cv2.waitKey(3000) # 1msec待つ
		ret, thresh1 = cv2.threshold(target_gray, 230, 255, cv2.THRESH_BINARY)

		# マップ名を判断
		inp = thresh1
		for map in self.map_list:
			mask_img = map['mask']
			out = inp + mask_img
			hist = cv2.calcHist([out], [0], None, [3], [0, 256])

			match = hist[2] / np.sum(hist) * 100

			if match > 99.0:
				hist2 = cv2.calcHist([inp], [0], None, [3], [0, 256])
				match2 = hist2[2] / np.sum(hist2) * 100
				#print("false-positive チェック match2: %f" % match2)
				if match2 > 90.0:
					match = 0

			if match > 99.0:
				#print("マップ名 %s : %f" % (map['name'], match))
				return map

			#cv2.imshow('Scene', thresh1)
			#k = cv2.waitKey(3000) # 1msec待つ
		return None

	def guess_mode(self, frame):
		cropped = frame[self.modename_top : self.modename_bottom, self.modename_left : self.modename_right]
		target_gray = cv2.cvtColor(cropped, cv2.COLOR_BGR2GRAY)
		#cv2.imshow('Scene', target_gray)
		#k = cv2.waitKey(3000) # 1msec待つ
		ret, thresh1 = cv2.threshold(target_gray, 230, 255, cv2.THRESH_BINARY)

		# モード名を判断
		inp = thresh1
		for mode in self.mode_list:
			mask_img = mode['mask']
			out = inp + mask_img
			hist = cv2.calcHist([out], [0], None, [3], [0, 256])
			match = hist[2] / np.sum(hist) * 100

			if match > 99.0:
				hist2 = cv2.calcHist([inp], [0], None, [3], [0, 256])
				match2 = hist2[2] / np.sum(hist2) * 100
				#print("false-positive チェック match2: %f" % match2)
				if match2 > 90.0:
					match = 0

			if match > 99.0:
				#print("モード名 %s : %f" % (mode['name'], match))
				return mode
		
			#cv2.imshow('Scene', thresh1)
			#k = cv2.waitKey(3000) # 1msec待つ
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
