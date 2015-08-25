#!/usr/bin/env python3
# -*- coding: utf-8 -*-
#
#  IkaLog
#  ======
#  Copyright (C) 2015 Takeshi HASEGAWA
#
#  Licensed under the Apache License, Version 2.0 (the "License");
#  you may not use this file except in compliance with the License.
#  You may obtain a copy of the License at
#
#      http://www.apache.org/licenses/LICENSE-2.0
#
#  Unless required by applicable law or agreed to in writing, software
#  distributed under the License is distributed on an "AS IS" BASIS,
#  WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
#  See the License for the specific language governing permissions and
#  limitations under the License.
#

from IkaUtils import *

## IkaOutput_Fluentd: IkaLog Output Plugin for Fluentd ecosystem
#
class IkaOutput_Fluentd:

	##
	# Log a record to Fluentd.
	# @param self       The Object Pointer.
	# @param recordType Record Type (tag)
	# @param record     Record
	#
	def submitRecord(self, recordType, record):
		try:
			from fluent import sender
			from fluent import event
			if self.host is None:
				sender = sender.setup(self.tag)
			else:
				sender.setup(self.tag, host = self.host, port = self.port)

			event.Event(recordType, record)
		except:
			printf("Fluentd: Failed to submit a record")

	##
	# Generate a record for onGameIndividualResult.
	# @param self      The Object Pointer.
	# @param context   IkaLog context
	#
	def getRecordGameIndividualResult(self, context):
		map = IkaUtils.map2text(context['game']['map'])
		rule = IkaUtils.rule2text(context['game']['rule'])
		won = IkaUtils.getWinLoseText(context['game']['won'], win_text ="win", lose_text = "lose", unknown_text = "unknown")
		return {
			'username': self.username,
			'map': map,
			'rule': rule,
			'result': won
		}

	##
	# onGameIndividualResult Hook
	# @param self      The Object Pointer
	# @param context   IkaLog context
	#
	def onGameIndividualResult(self, context):
		record = self.getRecordGameIndividualResult(context)
		self.submitRecord('gameresult', record)

	##
	# Check availability of modules this plugin depends on.
	# @param self      The Object Pointer.
	#
	def checkImport(self):
		try:
			from fluent import sender
			from fluent import event
		except:
			print("モジュール fluent-logger がロードできませんでした。 Fluentd 連携ができません。")
			print("インストールするには以下のコマンドを利用してください。\n    pip install fluent-logger\n")

	##
	# Constructor
	# @param self     The Object Pointer.
	# @param tag      tag
	# @param username Username of the player.
	# @param host     Fluentd host if Fluentd is on a different node
	# @param port     Fluentd port
	# @param username Name the bot use on Slack
	#
	def __init__(self, tag = 'ikalog', username = 'ika', host = None, port = 24224):
		self.tag = tag
		self.username = username
		self.host = host
		self.port = port

		self.checkImport()

if __name__ == "__main__":
	obj = IkaOutput_Fluentd()
