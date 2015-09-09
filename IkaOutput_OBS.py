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

import traceback
import time
import threading
import sys
import os
from datetime import datetime
from IkaUtils import *

## IkaLog Output Plugin: Show message on Console
#
class IkaOutput_OBS:

	## Generate new MP4 filename.
	#
	# @param self    The object.
	# @param context IkaLog context.
	# @return        File name generated (without directory/path)
	def createMP4Filename(self, context):
		map = IkaUtils.map2text(context['game']['map'], unknown = 'マップ不明')
		rule = IkaUtils.rule2text(context['game']['rule'], unknown = 'ルール不明')
		won = IkaUtils.getWinLoseText(context['game']['won'], win_text = 'win', lose_text = 'lose')

		time_str = time.strftime("%Y%m%d_%H%M", time.localtime())
		newname = '%s_%s_%s_%s.mp4' % (time_str, map, rule, won)

		return newname

	## RunControlOBS
	def runControlOBS(self, mode):
		cmd = '%s %s' % (self.ControlOBS, mode)
		print('Running %s' % cmd)
		try:
			os.system(cmd)
		except:
			print(traceback.format_exc())

	## OnLobbyMatched
	#
	# @param self    The object.
	# @param context IkaLog context.
	def onLobbyMatched(self, context):
		self.runControlOBS('start')

	def worker(self):
		self.runControlOBS('stop')

	def onGameIndividualResult(self, context):
		# Set Environment variables.
		map = IkaUtils.map2text(context['game']['map'], unknown = 'unknown')
		rule = IkaUtils.rule2text(context['game']['rule'], unknown = 'unknown')
		won = IkaUtils.getWinLoseText(context['game']['won'], win_text ='win', lose_text = 'lose', unknown_text = 'unknown')

		os.environ['IKALOG_STAGE'] = map
		os.environ['IKALOG_RULE'] = rule
		os.environ['IKALOG_WON'] = won
		#os.environ['IKALOG_TIMESTAMP'] = time.strftime("%Y%m%d_%H%M", context['game']['timestamp'])

		if not self.dir is None:
			os.environ['IKALOG_MP4_DESTNAME'] = '%s%s' % (self.dir, self.createMP4Filename(context))
			os.environ['IKALOG_MP4_DESTDIR'] = self.dir 

		# Since we want to stop recording asyncnously,
		# This function is called by independent thread.
		# Note the context can be unexpected value.

		thread = threading.Thread(target=self.worker)
		thread.start()

	def __init__(self, ControlOBS, dir = None):
		self.ControlOBS = ControlOBS
		self.dir = dir

if __name__ == "__main__":
	from datetime import datetime
	import time
	context = {
		'game': {
			'map': { 'name': 'mapname' },
			'rule': { 'name': 'rulename' },
			'won': True,
			'timestamp': datetime.now(),
		}
	}
			
	obs = IkaOutput_OBS('P:/IkaLog/utils/ControlOBS.au3', dir = 'K:/')
	
	obs.onLobbyMatched(context)
	time.sleep(10)
	obs.onGameIndividualResult(context)
