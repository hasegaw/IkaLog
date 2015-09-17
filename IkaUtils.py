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
from __future__ import print_function

import numpy as np
import cv2
import sys
import os
import re

class IkaUtils:
	@staticmethod
	def isWindows():
		try:
			os.uname()
		except AttributeError:
			return True
		return False

	@staticmethod
	def dprint(text):
		print(text, file = sys.stderr)

	## Find the local player.
	#
	# @param context   IkaLog Context.
	# @return The player information (Directionary class) if found.
	@staticmethod
	def getMyEntryFromContext(context):
		for e in context['game']['players']:
			if e['me']:
				return e
		return None

	## Get player's title.
	#
	# @param playerEntry The player.
	# @return Title in string. Returns None if playerEntry doesn't have title data.
	@staticmethod
	def playerTitle(playerEntry):
		if playerEntry is None:
			return None

		if not (('gender' in playerEntry) and ('prefix' in playerEntry)):
			return None

		prefix = re.sub('の', '', playerEntry['prefix'])
		return "%s%s" % (prefix, playerEntry['gender'])

	@staticmethod
	def map2text(map, unknown = None, lang = "ja"):
		if map is None:
			if unknown is None:
				unknown = "?"
			return unknown
		return map['name']

	@staticmethod
	def rule2text(rule, unknown = None, lang = "ja"):
		if rule is None:
			if unknown is None:
				unknown = "?"
			return unknown
		return rule['name']

	@staticmethod
	def cropImageGray(img, left, top, width, height):
		if len(img.shape) > 2 and img.shape[2] != 1:
			return cv2.cvtColor(
					img[top:top + height, left:left + width],
					cv2.COLOR_BGR2GRAY
			)
		return img[top:top + height, left:left + width]

	@staticmethod
	def matchWithMask(img, mask, threshold = 99.0, orig_threshold = 70.0, debug = False):
		if len(img.shape) > 2 and img.shape[2] != 1:
			img = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)

		# Check false-positive
		orig_hist = cv2.calcHist([img], [0], None, [3], [0, 256])
		match2 = orig_hist[2] / np.sum(orig_hist)

		if match2 > orig_threshold:
			# False-Positive condition.
			#print("original %f > orig_threshold %f" % (match2, orig_threshold))
			return False

		ret, thresh1 = cv2.threshold(img, 230, 255, cv2.THRESH_BINARY)
		added = thresh1 + mask
		hist = cv2.calcHist([added], [0], None, [3], [0, 256])

		match = hist[2] / np.sum(hist)

		if debug and (match > threshold):
			print("match2 %f match %f > threshold %f" % (match2, match, threshold))
			cv2.imshow('match_img', img)
			cv2.imshow('match_mask', mask)
			cv2.imshow('match_added', added)
			#cv2.waitKey()

		return match > threshold

	@staticmethod
	def loadMask(file, left, top, width, height):
		mask = cv2.imread(file)
		if mask is None:
			print("マスクデータ %s のロードに失敗しました")
			# raise a exception

		mask = mask[top:top + height, left:left + width]

		# BGR to GRAY
		if mask.shape[2] > 1:
			mask = cv2.cvtColor(mask, cv2.COLOR_BGR2GRAY)

		return mask 

	@staticmethod
	def getWinLoseText(won, win_text = "勝ち", lose_text = "負け", unknown_text = "不明"):
		if won is None:
			return unknown_text
		return win_text if won else lose_text

	@staticmethod
	def writeScreenshot(destfile, frame):
		try:
			cv2.imwrite(destfile, frame)
			return os.path.isfile(destfile)

		except:
			print("Screenshot: failed")
			return False


## Match images with mask data.
class IkaMatcher:
	## Match the image.
	# @param self   The object.
	# @param img    Frame data.
	# @param debug  If true, show debug information.
	def match(self, img, debug = None):
		if debug is None:
			debug = self.debug

		# Crop
		cropped = (img.shape[0] == self.height) and (img.shape[1] == self.width)
		if not cropped:
			img = img[self.top: self.top + self.height, self.left: self.left + self.width]

		# Grayscale
		if img.shape[2] > 1:
			img = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)

		# Check false-positive
		orig_hist = cv2.calcHist([img], [0], None, [3], [0, 256])
		orig_raito  = orig_hist[2] / np.sum(orig_hist)
		raito = 0

		match = True

		if orig_raito > self.orig_threshold:
			if debug:
				#print("original image exceeded orig_threshold")
				match = False

		if match and not (self.pre_threshold_value is None):
			ret, img = cv2.threshold(img, self.pre_threshold_value, 255, cv2.THRESH_BINARY)

		if match:
			added = img + self.mask_img

			hist = cv2.calcHist([added], [0], None, [3], [0, 256])

			raito = hist[2] / np.sum(hist)
			match = raito > self.threshold
		else:
			added = None

		if debug:# and (match > threshold):
			label = self.label if not self.label is None else self
			print("%s(%s): result=%s raito %f orig_raito %f, threshold %3.3f orig_threshold %3.3f" %
				(self.__class__.__name__, label, match, raito, orig_raito, self.threshold, self.orig_threshold))
			cv2.imshow('img: %s' % label, img)
			cv2.imshow('mask: %s' % label, self.mask_img)
			if not added is None:
				cv2.imshow('result: %s' % label, added)

		return match

	## Constructor.
	# @param self                 The object.
	# @param left                 Left of the mask.
	# @param top                  Top of the mask.
	# @param width                Width of the mask.
	# @param height               Height of the mask.
	# @param img                  Instance of the mask image.
	# @param img_file             Filename of the mask image.
	# @param threshold            Threshold
	# @param orig_threshold       Target frame must be lower than this raito.
	# @prram pre_threshold_value  Threshold target frame with this level before matching.
	# @param debug                If true, show debug information.
	# @param label                Label (text data) to distingish this mask.
	def __init__(self, left, top, width, height, img = None, img_file = None, threshold = 0.9, orig_threshold = 0.7, pre_threshold_value = 230, debug = False, label = None):
		self.top = top
		self.left = left
		self.width = width
		self.height = height
		self.threshold = threshold
		self.orig_threshold = orig_threshold
		self.pre_threshold_value = pre_threshold_value
		self.debug = debug
		self.label = label

		if not img_file is None:
			img = cv2.imread(img_file)

		if img is None:
			raise Exception('Could not load mask image')

		if len(img.shape) > 2 and img.shape[2] != 1:
			img = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)

		cropped = (img.shape[0] == self.height) and (img.shape[1] == self.width)
		if cropped:
			self.mask_img = img
		else:
			self.mask_img = img[top: top + height, left: left + width]
