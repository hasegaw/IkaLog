#!/usr/bin/env python3
# -*- coding: utf-8 -*-
import numpy as np
import cv2
import time

from IkaScene_GameStart import *
from IkaScene_ResultDetail import *
from IkaScene_InGame import *
from IkaConfig import *

capture, OutputPlugins = IkaConfig().config()

def core():
	context = {
		"game": {
			'map': None,
			'rule': None,
		},
		"engine": {
			'frame': None,
		}
	}

	last_capture = time.time() - 100;
	last_gamestart = time.time() - 100;

	scn_gamestart = IkaScene_GameStart()
	scn_gameresult = IkaScene_ResultDetail()
	scn_ingame = IkaScene_InGame()

	while True:
		# 0.5フレームおきに処理
		for i in range(12):
			frame = capture.read()

		while frame is None:
			cv2.waitKey(1000)
			frame = capture.read()

		context['engine']['frame'] = frame
		context['engine']['inGame'] = scn_ingame.matchTimerIcon(frame = frame)

		for op in OutputPlugins:
			if hasattr(op, "onFrameRead"):
				op.onFrameRead(context)

		# GameStart (マップ名、ルール名が表示されている) ?

		r = None
		if (not context['engine']['inGame']) and (time.time() - last_gamestart) > 10:
			r = scn_gamestart.match(context)

		if r:
			while (r):
				frame = capture.read()
				frame = capture.read()
				frame = capture.read()
				context['engine']['frame'] = frame
				r = scn_gamestart.match(context)

			last_gamestart = time.time()	

			for op in OutputPlugins:
				if hasattr(op, "onGameStart"):
					op.onGameStart(context)
		
		# GameResult (勝敗の詳細が表示されている）?
		r = False
		#if not thisFrame_InGameTimerIcon:
		r = scn_gameresult.match(context)

		if r:
			if ((time.time() - last_capture) > 60):
				last_capture = time.time()	
				
				# 安定するまで待つ
				for x in range(10):
					new_frame = capture.read()
					if not (new_frame is None):
						frame = new_frame

				# 安定した画像で再度解析
				context['engine']['frame'] = frame
				scn_gameresult.analyze(context)

				for op in OutputPlugins:
					if hasattr(op, "onGameIndividualResultAnalyze"):
						op.onGameIndividualResultAnalyze(context)

				for op in OutputPlugins:
					if hasattr(op, "onGameIndividualResult"):
						op.onGameIndividualResult(context)

				for op in OutputPlugins:
					if hasattr(op, "onGameReset"):
						op.onGameReset(context)

				context['game']['map'] = None
				context['game']['rule'] = None
				context['game']['won'] = None
				context['game']['players'] = None

		key = None

		for op in OutputPlugins:
			if hasattr(op, "onFrameNext"):
				key = op.onFrameNext(context)

		for op in OutputPlugins:
			if hasattr(op, "onKeyPress"):
				op.onKeyPress(context, key)

	# キャプチャを解放する
	#cap.release()
	cv2.destroyAllWindows()

core()
