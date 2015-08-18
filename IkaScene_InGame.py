#!/usr/local/bin/python3
# -*- coding: utf-8 -*-
import numpy as np
import cv2
import time
import sys
from IkaUtils import *

class IkaScene_InGame:
	# 720p サイズでの値
	timer_left = 60
	timer_width = 28
	timer_top = 28
	timer_height = 34

	def matchTimerIcon(self, frame = None, frame_gray = None):
		if frame_gray is None:
			src = frame
		else:
			src = frame_gray	
		
		img = IkaUtils.cropImageGray(
			src, self.timer_left, self.timer_top, self.timer_width, self.timer_height
		)

		return IkaUtils.matchWithMask(img, self.mask_timer, 0.85, 0.6)

	def __init__(self):
		self.mask_timer = IkaUtils.loadMask('masks/ingame_timer.png', self.timer_left, self.timer_top, self.timer_top, self.timer_height)

		#img = cv2.imread('masks/ingame_timer.png')
		#if img is None:
		#	print("マスクデータ masks/ingame_timer.png が読み込めませんでした")
		#self.mask_timer = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)[self.timer_top:self.timer_bottom, self.timer_left:self.timer_right]


if __name__ == "__main__":
	print(sys.argv)
	target = cv2.imread(sys.argv[1])

	obj = IkaScene_InGame()

	r = obj.matchTimerIcon(frame = target)

	print(r)

