#!/usr/bin/env python3
# -*- coding: utf-8 -*-
#
# Post game results to Slack, using Incoming Hook
#

class IkaOutput_Slack:
	def onGameStart(self, frame, map_name, mode_name):
		pass

	def onResultDetail(self, frame, map_name, mode_name, won):
		s_won = "勝ち" if won else "負け"
		s = "%sで%sに%sました" % (map_name, mode_name, s_won)

		try:
			import slackweb
			slack = slackweb.Slack(url = self.url)
			slack.notify(text = s, username = self.username)
		finally:
			pass

	def checkImport(self):
		try:
			import slackweb
		except:
			print("モジュール slackweb がロードできませんでした。 Slack 投稿ができません。")
			print("インストールするには以下のコマンドを利用してください。\n    pip install slackweb\n")
		finally:
			pass

	def __init__(self, url = None, username = "＜8ヨ"):
		self.url = url
		self.username = username

		self.checkImport()

