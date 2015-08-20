#!/usr/bin/env python3
# -*- coding: utf-8 -*-
import numpy as np
import cv2
import sys
from IkaUtils import *

class IkaScene_ResultDetail:

	def isEntryMe(self, entry_img):
		# ヒストグラムから、入力エントリが自分かを判断
		if len(entry_img.shape) > 2 and entry_img.shape[2] != 1:
			me_img = cv2.cvtColor(entry_img[:, 0:43], cv2.COLOR_BGR2GRAY)
		else:
			me_img = entry_img[:, 0:43]

		ret, me_img = cv2.threshold(me_img, 230, 255, cv2.THRESH_BINARY)

		me_score = np.sum(me_img)
		me_score_normalized = 0
		try:
			me_score_normalized = me_score / (43 * 45 * 255 / 10)
		except ZeroDivisionError as e:
			me_score_normalized = 0
		#print("score=%3.3f" % me_score_normalized)

		return (me_score_normalized > 1)

	def analyzeEntry(self, img_entry):
		# 各プレイヤー情報のスタート左位置
		entry_left = 610
		# 各プレイヤー情報の横幅
		entry_width = 610
		# 各プレイヤー情報の高さ
		entry_height = 46
		
		# 各エントリ内での名前スタート位置と長さ
		entry_xoffset_weapon = 760 - entry_left
		entry_xoffset_weapon_me = 719 - entry_left
		entry_width_weapon = 47

		entry_xoffset_name = 809 - entry_left
		entry_xoffset_name_me = 770 - entry_left
		entry_width_name = 180

		entry_xoffset_nawabari_score = 995 - entry_left
		entry_width_nawabari_score = 115

		entry_xoffset_kd = 1187 - entry_left
		entry_width_kd = 30
		entry_height_kd = 21

		me = self.isEntryMe(img_entry)
		if me:
			weapon_left = entry_xoffset_weapon_me
			name_left = entry_xoffset_name_me
			rank_left = 0
		else:
			weapon_left = entry_xoffset_weapon
			name_left = entry_xoffset_name
			rank_left = 43

		img_rank   = img_entry[20:45, rank_left:rank_left+43]
		img_weapon = img_entry[:, weapon_left:weapon_left + entry_width_weapon]
		img_name   = img_entry[:, name_left:name_left + entry_width_name]
		img_score  = img_entry[:, entry_xoffset_nawabari_score:entry_xoffset_nawabari_score + entry_width_nawabari_score]
		img_kills  = img_entry[0:entry_height_kd, entry_xoffset_kd:entry_xoffset_kd + entry_width_kd]
		img_deaths = img_entry[entry_height_kd:entry_height_kd * 2, entry_xoffset_kd:entry_xoffset_kd + entry_width_kd]

		return {
			"me": me,
			"img_rank": img_rank,
			"img_weapon": img_weapon,
			"img_name": img_name,
			"img_score": img_score,
			"img_kills": img_kills,
			"img_deaths": img_deaths,
		}

	def isWin(self, context):
		return context['game']['won']

	def analyze(self, context):
		# 各プレイヤー情報のスタート左位置
		entry_left = 610
		# 各プレイヤー情報の横幅
		entry_width = 610
		# 各プレイヤー情報の高さ
		entry_height = 45
		entry_top = [101, 166, 231, 296, 431, 496, 561, 626]

		entry_id = 0

		context['game']['players'] = []

		img = context['engine']['frame']
		for top in entry_top:
			entry_id = entry_id + 1
			img_entry = img[top:top+entry_height, entry_left:entry_left+entry_width]

			e = self.analyzeEntry(img_entry)
			e['team'] = 1 if entry_id < 4 else 2
			e['rank_in_team'] = (entry_id % 5) + 1
			context['game']['players'].append(e)

			if 0:
				for x in ['rank', 'weapon', 'name', 'score', 'kills', 'deaths']:
					cv2.imwrite("_%s.%d.png" % (x, entry_id), e['img_%s' % x])

			if e['me']:
				context['game']['won'] = True if entry_id < 5 else False
		context['game']['won'] = self.isWin(context)

	def match(self, context):
		return IkaUtils.matchWithMask(context['engine']['frame'], self.winlose_gray, 0.997, 0.20)

	def __init__(self):
		winlose = cv2.imread('masks/result_detail.png')
		if winlose is None:
			print("勝敗画面のマスクデータが読み込めませんでした。")

		self.winlose_gray = cv2.cvtColor(winlose, cv2.COLOR_BGR2GRAY)

if __name__ == "__main__":
	target = cv2.imread(sys.argv[1])
	obj = IkaScene_ResultDetail()

	context = {
		'engine': { 'frame': target },
		'game': {},
	}

	matched = obj.match(context)
	analyzed = obj.analyze(context)
	won = IkaUtils.getWinLoseText(context['game']['won'], win_text ="win", lose_text = "lose", unknown_text = "unknown")
	print("matched %s analyzed %s result %s" % (matched, analyzed, won))

