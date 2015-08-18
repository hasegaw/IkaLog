#!/usr/local/bin/python3
# -*- coding: utf-8 -*-

from datetime import datetime
import time

class IkaOutput_CSV:
	def onGameStart(self, frame, map_name, mode_name):
		pass

	def onResultDetail(self, frame, map_name, mode_name, won):
		t = datetime.now()
		t_str = t.strftime("%Y,%m,%d,%H,%M")
		t_unix = int(time.mktime(t.timetuple()))
		s_won = "勝ち" if won else "負け"
		record = "%s,%s,%s,%s,%s\n" % (t_unix,t_str, map_name, mode_name, s_won)
		try:
			csv_file = open(self.csv_filename, "a")
			csv_file.write(record)
			csv_file.close
		finally:
			pass

	def __init__(self, csv_filename):
		self.csv_filename = csv_filename
