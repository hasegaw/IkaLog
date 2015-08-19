#!/usr/bin/env python3
# -*- coding: utf-8 -*-


from IkaUtils import *

## IkaOutput_Slack: IkaLog Output Plugin for Slack
#
# Post game results to Slack, using Incoming Hook
class IkaOutput_Slack:

	## postRecord
	#
	# Post a bot message to slack.
	# @param self     The Object Pointer.
	# @param text     Text message.
	# @param username Username.
	def postRecord(self, text = "", username = "＜8コ三"):
		try:
			import slackweb
			slack = slackweb.Slack(url = self.url)
			slack.notify(text = text, username = self.username)
		finally:
			pass

	## GameStart Hook
	#
	# @param self      The Object Pointer
	# @param frame     Screenshot image
	# @param map_name  Map name.
	# @param mode_name Mode name.
	def onGameStart(self, frame, map_name, mode_name):
		pass

	## getRecordResultDetail
	#
	# Generate a message for ResultDetail.
	# @param self      The Object Pointer.
	# @param map_name  Map name.
	# @param mode_name Mode name.
	# @param won       True is player's team won. Otherwise False.
	def getRecordResultDetail(self, map_name, mode_name, won):
		s_won = IkaUtils.getWinLoseText(won, win_text ="勝ち", lose_text = "負け", unknown_text = "不明")
		return "%sで%sに%sました" % (map_name, mode_name, s_won)

	## ResultDetail Hook
	#
	# @param self      The Object Pointer
	# @param frame     Screenshot image
	# @param map_name  Map name
	# @param mode_name Mode name
	def onResultDetail(self, frame, map_name, mode_name, won):
		s = self.getRecordResultDetail(map_name, mode_name, won)
		self.postRecord(text = s, username = self.username)

	## checkImport
	#
	# Check availability of modules this plugin depends on.
	# @param self      The Object Pointer.
	def checkImport(self):
		try:
			import slackweb
		except:
			print("モジュール slackweb がロードできませんでした。 Slack 投稿ができません。")
			print("インストールするには以下のコマンドを利用してください。\n    pip install slackweb\n")
		finally:
			pass

	## Constructor
	#
	# @param self     The Object Pointer.
	# @param url      Slack Incoming Hook Endpoint
	# @param username Name the bot use on Slack
	def __init__(self, url = None, username = "＜8ヨ"):
		self.url = url
		self.username = username
		self.checkImport()
