#!/usr/bin/env python3
# -*- coding: utf-8 -*-

from IkaUtils import *

## IkaOutput_Fluentd: IkaLog Output Plugin for Fluentd ecosystem
#
class IkaOutput_Fluentd:

	def submitRecord(self, recordType, record):
		try:
			from fluent import sender
			from fluent import event
			if self.host is None:
				sender = sender.setup(self.tag)
			else:
				sender.setup(self.tag, host = self.host, port = self.port)

			event.Event(recordType, record)
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
		s_won = IkaUtils.getWinLoseText(won, win_text ="win", lose_text = "lose", unknown_text = "unknown")
		return {
			'username': self.username,
			'map': map_name,
			'mode': mode_name,
			'result': s_won
		}

	## ResultDetail Hook
	#
	# @param self      The Object Pointer
	# @param frame     Screenshot image
	# @param map_name  Map name
	# @param mode_name Mode name
	def onResultDetail(self, frame, map_name, mode_name, won):
		record = self.getRecordResultDetail(map_name, mode_name, won)
		self.submitRecord('gameresult', record)

	## checkImport
	#
	# Check availability of modules this plugin depends on.
	# @param self      The Object Pointer.
	def checkImport(self):
		try:
			from fluent import sender
			from fluent import event
		except:
			print("モジュール fluent-logger がロードできませんでした。 Fluentd 連携ができません。")
			print("インストールするには以下のコマンドを利用してください。\n    pip install fluent-logger\n")
		finally:
			pass

	## Constructor
	#
	# @param self     The Object Pointer.
	# @param tag      tag
	# @param username Username of the player.
	# @param host     Fluentd host if Fluentd is on a different node
	# @param port     Fluentd port
	# @param username Name the bot use on Slack
	def __init__(self, tag = 'ikalog', username = 'ika', host = None, port = 24224):
		self.tag = tag
		self.username = username
		self.host = host
		self.port = port

		self.checkImport()

if __name__ == "__main__":
	obj = IkaOutput_Fluentd()
	obj.onResultDetail(None, 'mapName', 'modeName', True)
