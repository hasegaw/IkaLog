#!/usr/bin/env python3
# -*- coding: utf-8 -*-

from IkaUtils import *
from datetime import datetime
import time

## IkaLog Output Plugin: Show message on Console
#
class IkaOutput_Console:

	##
	# onGameStart Hook
	# @param self      The Object Pointer
	# @param context   IkaLog context
	#
	def onGameStart(self, context):
		map = IkaUtils.map2text(context['game']['map'])
		rule = IkaUtils.rule2text(context['game']['rule'])
		print("ゲームスタート。マップ %s ルール %s" % (map, rule))

	##
	# Generate a message for onGameIndividualResult.
	# @param self      The Object Pointer.
	# @param context   IkaLog context
	#
	def getTextGameIndividualResult(self, context):
		map = IkaUtils.map2text(context['game']['map'])
		rule = IkaUtils.rule2text(context['game']['rule'])
		won = IkaUtils.getWinLoseText(context['game']['won'], win_text ="勝ち", lose_text = "負け", unknown_text = "不明")
		t = datetime.now()
		t_str = t.strftime("%Y,%m,%d,%H,%M")
		t_unix = int(time.mktime(t.timetuple()))

		return "ゲーム終了。マップ %s ルール %s 結果 %s" % (map, rule, won)

	##
	# onGameIndividualResult Hook
	# @param self      The Object Pointer
	# @param context   IkaLog context
	#
	def onGameIndividualResult(self, context):
		s = self.getTextGameIndividualResult(context)
		print(s)
