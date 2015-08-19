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
	last_capture = time.time() - 100;
	last_gamestart = time.time() - 100;

	_map = None
	_mode = None

	current_map = None
	current_mode = None

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

		thisFrame_InGameTimerIcon = scn_ingame.matchTimerIcon(frame = frame)

		# GameStart (マップ名、ルール名が表示されている) ?

		r = None
		if (not thisFrame_InGameTimerIcon) and (time.time() - last_gamestart) > 10:
			r = scn_gamestart.match(frame)

		if r:
			while (r):
				frame = capture.read()
				frame = capture.read()
				frame = capture.read()
				r = scn_gamestart.match(frame)
				if r:
					if current_map is None:
						current_map = r['map']
					if current_mode is None:
						current_mode = r['mode'] 

			last_gamestart = time.time()	

			_map = current_map['name'] if current_map else 'スプラトゥーン'
			_mode = current_mode['name'] if current_mode else 'バトル'

			for op in OutputPlugins:
				try:
					op.onGameStart(frame, _map, _mode)
				finally:
					pass
			continue
		
		# GameResult (勝敗の詳細が表示されている）?
		r = False
		if not thisFrame_InGameTimerIcon:
			r = scn_gameresult.match(frame)

		if r:
			if ((time.time() - last_capture) > 60):
				last_capture = time.time()	
				
				# 安定するまで待つ
				for x in range(10):
					new_frame = capture.read()
					if not (new_frame is None):
						frame = new_frame

				win = scn_gameresult.isWin(frame)
				for op in OutputPlugins:
					op.onResultDetail(frame, _map, _mode, win)

				current_map = None
				current_mode = None


		cv2.imshow('IkaLog', frame)
		k = cv2.waitKey(1) # 1msec待つ
		# if k == 27: # ESCキーで終了
		# 	break

	# キャプチャを解放する
	#cap.release()
	cv2.destroyAllWindows()

core()
