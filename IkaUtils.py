#!/usr/bin/env python3
import numpy as np
import cv2

class IkaUtils:

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
