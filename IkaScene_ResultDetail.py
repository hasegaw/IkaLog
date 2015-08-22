#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import json
import numpy as np
import cv2
import sys
from IkaWeaponsChecker import *
from IkaUtils import *
from IkaPositionGenerator import *

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

	def analyzeEntry(self, img, idx):
		def getImage(img, pos):
			return img[int(pos.top()):int(pos.bottom()), int(pos.left()):int(pos.right())]

		player = self.posgen.getPlayerPositionGenerator(idx, False)
		pos = player.getPlayerArea()
		is_me = self.isEntryMe(getImage(img, pos))
		
		player = self.posgen.getPlayerPositionGenerator(idx, is_me)
		rpos = player.getPlayerRankArea()
		wpos = player.getPlayerWeaponArea()
		npos = player.getPlayerNameArea()
		spos = player.getPlayerScoreArea()
		kpos = player.getPlayerKillCountArea()
		dpos = player.getPlayerDeathCountArea()
		return {
			"me": is_me,
			"img_rank": getImage(img, rpos),
			"img_weapon": getImage(img, wpos),
			"img_name": getImage(img, npos),
			"img_score": getImage(img, spos),
			"img_kills": getImage(img, kpos),
			"img_deaths": getImage(img, dpos),
		}

	def isWin(self, context):
		return context['game']['won']

	def analyze(self, context):
		context['game']['players'] = []

		img = context['engine']['frame']
		for entry_id in range(0, 8):
			e = self.analyzeEntry(img, entry_id)
			e['team'] = 1 if entry_id < 4 else 2
			e['rank_in_team'] = (entry_id % 5) + 1
			e['weapon'] = self.weapons_checker.getWeaponName(e['img_weapon'])
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
		winlose = cv2.imread('masks/result_detail.png', cv2.IMREAD_GRAYSCALE)
		if winlose is None:
			print('勝敗画面のマスクデータが読み込めませんでした。')
			
		self.winlose_gray = winlose

		self.posgen = IkaPositionGenerator(1280, 720)

		json_file = open('resources/res.json', 'r', encoding = 'utf-8')
		respack = json.load(json_file)
		json_file.close
		json_file2 = open('resources/lang-ja.json', 'r', encoding = 'utf-8')
		langpack = json.load(json_file2)
		json_file2.close
		self.weapons_checker = IkaWeaponsChecker(respack, langpack)

if __name__ == "__main__":
	target = cv2.imread(sys.argv[1])
	obj = IkaScene_ResultDetail()

	context = {
		'engine': { 'frame': target },
		'game': {},
	}

	matched = obj.match(context)
	analyzed = obj.analyze(context)
	won = IkaUtils.getWinLoseText(context['game']['won'], win_text = "win", lose_text = "lose", unknown_text = "unknown")
	print("matched %s analyzed %s result %s" % (matched, analyzed, won))

	i = 0
	for p in context['game']['players']:
		print("player[%d]: ブキ %s" % (i, p['weapon']))
		i += 1