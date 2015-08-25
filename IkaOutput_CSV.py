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
from datetime import datetime
import time

## @package IkaOutput_CSV

## IkaOutput_CSV: IkaLog CSV Output Plugin
#
# Log Splatoon game results as CSV format.
class IkaOutput_CSV:

	##
	# Write a line to text file.
	# @param self     The Object Pointer.
	# @param record   Record (text)
	#
	def writeRecord(self, record):
		try:
			csv_file = open(self.csv_filename, "a")
			csv_file.write(record)
			csv_file.close
		except:
			print("CSV: Failed to write CSV File")

	##
	# Generate a message for onGameIndividualResult.
	# @param self      The Object Pointer.
	# @param context   IkaLog context
	#
	def getRecordGameIndividualResult(self, context):
		map = IkaUtils.map2text(context['game']['map'])
		rule = IkaUtils.rule2text(context['game']['rule'])
		won = IkaUtils.getWinLoseText(context['game']['won'], win_text ="勝ち", lose_text = "負け", unknown_text = "不明")

		t = datetime.now()
		t_str = t.strftime("%Y,%m,%d,%H,%M")
		t_unix = int(time.mktime(t.timetuple()))
		s_won = IkaUtils.getWinLoseText(won, win_text ="勝ち", lose_text = "負け", unknown_text = "不明")

		return "%s,%s,%s,%s,%s\n" % (t_unix,t_str, map, rule, won)

	##
	# onGameIndividualResult Hook
	# @param self      The Object Pointer
	# @param context   IkaLog context
	#
	def onGameIndividualResult(self, context):
		record = self.getRecordGameIndividualResult(context)
		self.writeRecord(record)

	##
	# Constructor
	# @param self         The Object Pointer.
	# @param csv_filename CSV log file name
	#
	def __init__(self, csv_filename):
		self.csv_filename = csv_filename
