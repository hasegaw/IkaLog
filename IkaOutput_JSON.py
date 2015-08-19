#!/usr/bin/env python3
# -*- coding: utf-8 -*-

from datetime import datetime
import time
import json

## IkaOutput_CSV: IkaLog Output Plugin for CSV Logging
#
# Write JSON Log file
class IkaOutput_JSON:

	## writeRecord
	#
	# Write a line to text file.
	#
	# @param self     The Object Pointer.
	# @param record   Record (text)
	def writeRecord(self, record):
		try:
			json_file = open(self.json_filename, "a")
			json_file.write(record_str)
			json_file.close
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
		t = datetime.now()
		t_str = t.strftime("%Y,%m,%d,%H,%M")
		t_unix = int(time.mktime(t.timetuple()))
		s_won = IkaUtils.getWinLoseText(won, win_text ="win", lose_text = "lose", unknown_text = "unknown")

		record = { 'time': t_unix, 'event': 'GameResult', 'map': map_name, 'rule': mode_name, 'result': s_won }
		return json.dumps(record, separators=(',',':'))

	## onResultDetail
	#
	# ResultDetail Hook
	#
	# @param self      The Object Pointer
	# @param frame     Screenshot image
	# @param map_name  Map name
	# @param mode_name Mode name
	def onResultDetail(self, frame, map_name, mode_name, won):
		record = self.getRecordResultDetail(map_name, mode_name, won)
		self.writeRecord(record)

	## Constructor
	#
	# @param self          The Object Pointer.
	# @param json_filename JSON log file name
	def __init__(self, json_filename):
		self.json_filename = json_filename
