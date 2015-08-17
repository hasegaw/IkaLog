#!/usr/local/bin/python3
# -*- coding: utf-8 -*-
import numpy as np
import cv2
import sys

class IkaScene_ResultDetail:

	def isEntryMe(self, entry_img):
		# ヒストグラムから、入力エントリが自分かを判断
		me_img = entry_img[:, 0:43]

		me_score = np.sum(me_img)
		me_score_normalized = 0
		try:
			me_score_normalized = me_score / (43 * 45 * 255 / 10)
		except ZeroDivisionError as e:
			me_score_normalized = 0
		#print("score=%3.3f" % me_score_normalized)

		#cv2.imshow('Scene', me_img)
		#k = cv2.waitKey(1000) # 1msec待つ

		return (me_score_normalized > 1)

	def findMe(self, img_gray):
		# リザルト画面(720p)から自分を見つける
		# 入力 image は cv2.COLOR_BGR2GRAY であること
		ret, thresh1 = cv2.threshold(img_gray, 230, 255, cv2.THRESH_BINARY)

		# 各プレイヤー情報のスタート左位置
		entry_left = 610
		# 各プレイヤー情報の横幅
		entry_width = 610
		# 各プレイヤー情報の高さ
		entry_height = 45
		
		# 各エントリ内での名前スタート位置と長さ
		entry_xoffset_name = 809 - entry_left
		entry_xoffset_name_me = 770 - entry_left
		entry_width_name = 180
		
		entry_xoffset_nawabari_score = 995 - entry_left
		entry_width_nawabari_score = 115
		entry_top = [101, 167, 231, 296, 432, 496, 562, 627]

		entry_xoffset_kd = 1187 - entry_left
		entry_width_kd = 30
		entry_height_kd = 20
		
		entry_id = 0
		for top in entry_top:
			entry_id = entry_id + 1
			img_entry = thresh1[top:top+entry_height, entry_left:entry_left+entry_width]
			
			name_left = entry_xoffset_name
			rank_left =43
			if (self.isEntryMe(img_entry)):
				return entry_id

		return None

	def isWin(self, frame):
		gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
		index = self.findMe(gray)

		# プレイヤー1〜4のうちならWin
		return index and (index < 5)

	def match(self, frame):
		img_gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
		added = cv2.add(img_gray, self.winlose_gray)
		hist = cv2.calcHist([added], [0], None, [3], [0, 256])
		total = np.sum(hist)

		match = hist[2] / total * 100

		if (match > 99.9):
			# false-positive の可能性があるのでオリジナル画像の分布を確認
			hist2 = cv2.calcHist([img_gray], [0], None, [3], [0, 256])
			total2 = np.sum(hist2)
			match2 = hist2[2] / total2 * 100
			if (match2 > 20):
				# false-positive
				match = 0
				#print("false-positive")

		return match > 99.9

	def __init__(self):
		winlose = cv2.imread('masks/result_detail.png')
		if winlose is None:
			print("勝敗画面のマスクデータが読み込めませんでした。")
		self.winlose_gray = cv2.cvtColor(winlose, cv2.COLOR_BGR2GRAY)

if __name__ == "__main__":
	target = cv2.imread(sys.argv[1])
	obj = IkaScene_ResultDetail()

	print(obj.isWin(target))

