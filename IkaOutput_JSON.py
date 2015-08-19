#!/usr/bin/env python3
# -*- coding: utf-8 -*-

from datetime import datetime
import time
import json

class IkaOutput_JSON:
	def onGameStart(self, frame, map_name, mode_name):
		pass

	def onResultDetail(self, frame, map_name, mode_name, won):
		t = datetime.now()
		t_str = t.strftime("%Y,%m,%d,%H,%M")
		t_unix = int(time.mktime(t.timetuple()))
		s_won = "win" if won else "lose"

		record = { 'time': t_unix, 'event': 'GameResult', 'map': map_name, 'rule': mode_name, 'result': s_won }

		record_str = json.dumps(record, separators=(',',':'))

		try:
			json_file = open(self.json_filename, "a")
			json_file.write(record_str)
			json_file.close
		finally:
			pass

	def __init__(self, json_filename):
		self.json_filename = json_filename
