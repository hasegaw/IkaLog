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
import numpy as np
import cv2
import sys
from IkaUtils import *

class IkaScene_Lobby:
	def match(self, context):
		frame = context['engine']['frame']

		# 「ルール」「ステージ」の文字があればパブリックロビーで待ち合わせ中
		if not self.mask_rule.match(frame):
			return False

		if not self.mask_stage.match(frame):
			return False

		# マッチング状況はどちらかがあるはず
		r_matching = self.mask_matching.match(frame)
		r_matched  = self.mask_matched.match(frame)

		context['game']['lobby'] = {}
		context['game']['lobby']['public'] = True
		context['game']['lobby']['state'] = None

		if not (r_matching or r_matched):
			return False

		if (r_matching):
			context['game']['lobby']['state'] = 'matching'
		if (r_matched):
			context['game']['lobby']['state'] = 'matched'

		return True

	def __init__(self):
		self.mask_rule = IkaMatcher(
			0, 220, 737, 94,
			img_file = 'masks/ui_lobby_public.png',
			threshold = 0.999,
			orig_threshold = 0.5,
			pre_threshold_value = 220,
			label = 'Rule'
		)

		self.mask_stage = IkaMatcher(
			0, 345, 737, 94,
			img_file = 'masks/ui_lobby_public.png',
			threshold = 0.999,
			orig_threshold = 0.5,
			pre_threshold_value = 220,
			label = 'Stage'
		)

		self.mask_matching = IkaMatcher(
			826, 37, 280, 34,
			img_file = 'masks/ui_lobby_public2.png',
			threshold = 0.97,
			orig_threshold = 0.5,
			pre_threshold_value = 220,
			label = 'Matching',
		)

		self.mask_matched = IkaMatcher(
			826, 37, 280, 34,
			img_file = 'masks/ui_lobby_public_matched.png',
			threshold = 0.97,
			orig_threshold = 0.5,
			pre_threshold_value = 220,
			label = 'Matched',
			debug = True
		)

if __name__ == "__main__":
	target = cv2.imread(sys.argv[1])
	obj = IkaScene_Lobby()

	context = {
		'engine': { 'frame': target },
		'game': {},
	}

	matched = obj.match(context)
	print("matched %s" % (matched))
	print(context['game'])

	cv2.waitKey(10000)
