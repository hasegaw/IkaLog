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

import cv2
import sys
import numpy as np
import os
import pickle

## @package IkaGlyphRecoginizer

class IkaGlyphRecoginizer:
	## Maximum Hue Value in OpenCV HSV Color.
	_HSV_COLOR_MAX = 185 

	## Number of Hue samples
	_HSV_COLOR_SAMPLES =  64

	## Models
	models = []

	## pre-calculated Hue samples

	def calcurateHueSamples(self, num_colors):
		samples = []
		for i in range(num_colors):
			c_min = self._HSV_COLOR_MAX / num_colors * i
			c_max = self._HSV_COLOR_MAX / num_colors * (i + 1)
			if c_min == 0:
				c_min = 1
			samples.append((c_min, c_max))
		return samples

	## Normalize the image. (for weapons)
	#
	# - Crop the image
	# - Detect background color
	# - Replace the background color to black
	# - Replace white color to blue (0, 0, 255) because we want to compare using Hue value.
	#
	# @param img    the source image
	# @return (img,out_img)  the result
	def normalizeWeaponImage(self, img):
		img_h = img.shape[0]
		img_w = img.shape[1]
	
		#img = img[2:img_h - 4]
		img = img[2:img_h - 4, 5:img_w - 3]
		#img = img[2:img_h - 2, img_w * 0.2:img_w - 2]
	
		img_hsv = cv2.cvtColor(img, cv2.COLOR_BGR2HSV)
	
		h = img_hsv.shape[0]
		w = img_hsv.shape[1]
	
		bgcolor_sample = img_hsv[h - 3:h, 0:3, 0] # Hue
		bg_h_color = np.average(bgcolor_sample)
		rad = 7
		bg_h_color1 = int(bg_h_color - rad)
		bg_h_color2 = int(bg_h_color + rad)
	
		img_mask = cv2.inRange(img_hsv[:, :, 0], bg_h_color1, bg_h_color2)
		img_mask2 = 255 - cv2.inRange(img_hsv[:, :, 2], 165,255) # Visibility
		img_mask = np.minimum(img_mask, img_mask2)
		
		out_img = img.copy()
		for i in range(3):
			out_img[:, :, i] = np.minimum(out_img[:, :, i], 255 - img_mask)
	
		# 白いところを検出する (s が低く v が高い)
		white_mask_s = cv2.inRange(img_hsv[:, :, 1], 0, 48)
		white_mask_v = cv2.inRange(img_hsv[:, :, 2], 224, 256)
		white_mask = np.minimum(white_mask_s, white_mask_v)
	
		# 白色を置きかえ
		out_img[:, :, 0] = np.maximum(out_img[:, :, 0], white_mask)
		out_img[:, :, 1] = np.minimum(out_img[:, :, 1], 255 - white_mask)
		out_img[:, :, 2] = np.minimum(out_img[:, :, 2], 255 - white_mask)
	
		#cv2.imshow('orig', img)
		#cv2.imshow('H', img_h)
		#cv2.imshow('S', img_s)
		#cv2.imshow('V', img_v)
		#cv2.imshow('HSV', img_hsv)
		#cv2.imshow('mask', img_mask)
		#cv2.imshow('mask2', img_mask2)
		#cv2.waitKey()
		return [
			out_img,
			img,
		]
	
	def countH(self, img_h, samples):
		r = []
		for sample in samples:
			x = cv2.inRange(img_h, sample[0], sample[1])
			cond = x > 127
			r.append(len(np.extract(cond, img_h)))
		return r
	
	
	## Analyze a image.
	#
	def analyzeImage(self, img, blocks_x = 3, blocks_y = 3, debug = False):
		samples = self._precalculatedHueSamples

		imgs = self.normalizeWeaponImage(img)
		d = imgs[0]
		bw = int(d.shape[1] / blocks_x)
		bh = int(d.shape[0] / blocks_y)
	
		img_hsv = cv2.cvtColor(d, cv2.COLOR_BGR2HSV)
		img_h = img_hsv[:, :, 0]
		img_s = img_hsv[:, :, 1]
		img_v = img_hsv[:, :, 2]
	
		hist = []
		part_img_h = np.zeros((bh, bw), np.uint8)  #cv2.resize(img_h, (bw, bh))
		part_img_s = np.zeros((bh, bw), np.uint8)  #cv2.resize(img_h, (bw, bh))
	
		for bx in range(blocks_x):
			for by in range(blocks_y):
				x1 = bw * (bx + 0)
				x2 = bw * (bx + 1)
				y1 = bh * (by + 0)
				y2 = bh * (by + 1)
				part_img_h[:, :] = img_h[y1:y2, x1:x2]
				part_img_s[:, :] = img_s[y1:y2, x1:x2]
				hist.extend(self.countH(part_img_h, samples))
	
		param = { 'hist': np.array(hist).astype(dtype = np.float) }
		if (not debug):
			return param
	
		offset_w = 100#img_h.shape[1]
		new_w = offset_w + (len(hist) * 8)
		new_h = img.shape[0]
		dimg = cv2.resize(img, (new_w, new_h))
		dimg.fill(0)	
		dimg = cv2.cvtColor(dimg, cv2.COLOR_BGR2HSV)
	
		# カラーバーを書く
		for i in range(len(hist)):
			sample = samples[i % len(samples)]		
			c_avg = int((sample[0] + sample[1]) / 2)
	
			y1 = new_h - hist[i]
			y2 = new_h
			x1 = offset_w + 8 * (i + 0) 
			x2 = offset_w + 8 * (i + 1) 
	
			dimg[:, x1:x2, 0].fill(c_avg)
			dimg[:, x1:x2, 1].fill(255)
			dimg[:, x1:x2, 2].fill(0)
			dimg[y1:y2, x1:x2, 2].fill(255)
	
		dimg = cv2.cvtColor(dimg, cv2.COLOR_HSV2BGR)
		w = imgs[0].shape[1]
		h = imgs[0].shape[0]
		dimg[:h,:w] = imgs[0][:,:]
		dimg[:h,w:w*2] = imgs[1][:,:]
		cv2.imshow(':D', dimg)
		#cv2.waitKey(3000)
	
		return param, dimg
	
	
	def calculateParamersFromSamples(self, l_hist):
		num_samples = len(l_hist)
		colors = len(l_hist[0])
	
		a = np.array(l_hist).astype(dtype = np.float)
	#	print("num_samples = %d, colors = %d" % (num_samples, colors))
		#print(a)
		#print(len(a[:,1]))
	
		b = a.T
		#print(len(b[:,1]))
	
		h_avg = np.average(b, axis = 1)
		h_var = np.var(b, axis = 1)
		from pprint import pprint
		#pprint(h_avg)
		#pprint(h_var)
	
		for e in a:
			abs_val = np.abs(e - h_avg)
			cond = (abs_val < h_var)
	#		print(cond)
	
			n = len(np.extract(cond, cond))
	#		print(n)
	
		return { 'h_avg': h_avg, 'h_var': h_var }
	
	def matchImageWithParameter(self, img_param, trained):
		h_avg = trained['h_avg']
		h_var = trained['h_var']
	
		abs_val = np.abs(img_param['hist'] - h_avg)
	
	#	cond0 = (h_var < 256 )
		cond1 = (abs_val < (h_var))
		cond = cond1
	#	cond = np.logical_and(cond0, cond1)
	
		scores = np.minimum(1000, (abs_val / (h_var + 0.1))) * np.sqrt(h_avg)
	
	
		# 分散を使用した重み付け
		score = np.sum(np.extract(cond, scores))
		scores_max = np.sum(scores)
	
		#score = np.sum(np.extract(cond, scores))
		#scores_max = np.sum(np.extract(cond0, scores))
		score_normalized = (score * 100) / scores_max
	
		return score_normalized
		cv2.imshow(':D', img)
		#cv2.waitKey(1000)
	
	def showLearnedWeaponImage(self, l, name = 'hoge', save = None):
		new_h = l[0].shape[0] * len(l)
		new_w = l[0].shape[1]
	
		dest = cv2.resize(l[0], (new_w, new_h))
		dest.fill(0)
		y = 0
		for i in l:
			h = i.shape[0]
			dest[y:y + h] = i[0: h]
			y = y + h
	
		cv2.imshow(name, dest)
		if save:
			cv2.imwrite(save, dest)
	
	def learnImageGroup(self, name = None, dir = None):
		l = []
		l_hist = []
		samples = []
		for root, dirs, files in os.walk(dir):
			for file in files:
				if file.endswith(".png"):
					f = os.path.join(root, file)
					img = cv2.imread(f)
					samples.append(img)

					param, r = self.analyzeImage(img, debug = True)
					l.append(r)
					l_hist.append(param['hist'])
	
		self.showLearnedWeaponImage(l, name)
		trained = self.calculateParamersFromSamples(l_hist)
		model = { 'name': name, 'model': trained, 'samples': samples }

		self.models.append(model)
	
		return model 
	
	def guessImage1(self, img = None, img_param = None, model = None):
		if img_param is None:
			img_param = self.analyzeImage(img)
	
		return self.matchImageWithParameter(img_param, model['model'])
	
	def guessImage(self, img = None, img_param = None, models = None):
		if models is None:
			models = self.models

		if img_param is None:
			img_param = self.analyzeImage(img)
	
		result = { 'name': None, 'score': 0 }
		for model in models:
			s = self.guessImage1(img_param = img_param, model = model)
			if s > result['score']:
				result['score'] = s
				result['name'] = model['name']
			model_matched = model
		return (result, model)

	def stripModel(self):
		models = self.models.copy()
		for model in models:
			if "samples" in model:
				del model["samples"]
		return models

	def saveModelToFile(self, file):
		f = open(file, "wb")
		pickle.dump([self.stripModel()], f)
		f.close()

	def loadModelFromFile(self, file):
		f = open(file, "rb")
		l = pickle.load(f)
		f.close()
		self.models = l[0]

	def __init__(self):
		self._precalculatedHueSamples = self.calcurateHueSamples(self._HSV_COLOR_SAMPLES)

