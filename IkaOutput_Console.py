#!/usr/local/bin/python3
# -*- coding: utf-8 -*-

class IkaOutput_Console:
	def onGameStart(self, frame, map_name, mode_name):
		print("ゲームスタート。マップ %s ルール %s" % (map_name, mode_name))

	def onResultDetail(self, frame, map_name, mode_name, won):
		s_won = "勝ち" if won else "負け"
		print("ゲーム終了。マップ %s ルール %s 結果 %s" % (map_name, mode_name, s_won))

