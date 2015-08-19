#!/usr/bin/env python3
# -*- coding: utf-8 -*-

from IkaUtils import *
from datetime import datetime
import time

## @package IkaOutput_CSV

## IkaOutput_CSV: IkaLog CSV Output Plugin
#
# Log Splatoon game results as CSV format.
class IkaOutput_CSV:

	## writeRecord
	#
	# Write a line to text file.
	#
	# @param self     The Object Pointer.
	# @param record   Record (text)
	def writeRecord(self, record):
		try:
			csv_file = open(self.csv_filename, "a")
			csv_file.write(record)
			csv_file.close
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
		s_won = IkaUtils.getWinLoseText(won, win_text ="勝ち", lose_text = "負け", unknown_text = "不明")

		return "%s,%s,%s,%s,%s\n" % (t_unix,t_str, map_name, mode_name, s_won)

	## onResultDetail
	#
	# ResultDetail Hook
	#
	# @param self      The Object Pointer
	# @param frame     Screenshot image
	# @param map_name  Map name
	# @param mode_name Mode name
	# @param won       True if the player's team won. Otherwise False
	def onResultDetail(self, frame, map_name, mode_name, won):
		record = self.getRecordResultDetail(map_name, mode_name, won)
		self.writeRecord(record)

	## Constructor
	#
	# @param self         The Object Pointer.
	# @param csv_filename CSV log file name
	def __init__(self, csv_filename):
		self.csv_filename = csv_filename
