#!/usr/bin/env python3
# -*- coding: utf-8 -*-

from IkaUtils import *
from datetime import datetime
import time

## IkaLog Output Plugin: Show message on Cnosole
#
class IkaOutput_Console:
	## GameStart Hook
	#
	# @param self      The Object Pointer
	# @param frame     Screenshot image
	# @param map_name  Map name.
	# @param mode_name Mode name.
	def onGameStart(self, frame, map_name, mode_name):
		print("ゲームスタート。マップ %s ルール %s" % (map_name, mode_name))

	## getRecordResultDetail
	#
	# Generate a message for ResultDetail.
	# @param self      The Object Pointer.
	# @param map_name  Map name.
	# @param mode_name Mode name.
	# @param won       True if player's team won. Otherwise False.
	def getRecordResultDetail(self, map_name, mode_name, won):
		t = datetime.now()
		t_str = t.strftime("%Y,%m,%d,%H,%M")
		t_unix = int(time.mktime(t.timetuple()))

		s_won = IkaUtils.getWinLoseText(won, win_text ="勝ち", lose_text = "負け", unknown_text = "不明")
		return "ゲーム終了。マップ %s ルール %s 結果 %s" % (map_name, mode_name, s_won)

	## ResultDetail Hook
	#
	# @param self      The Object Pointer
	# @param frame     Screenshot image
	# @param map_name  Map name
	# @param mode_name Mode name
	def onResultDetail(self, frame, map_name, mode_name, won):
		s = self.getRecordResultDetail(map_name, mode_name, won)
		print(s)
