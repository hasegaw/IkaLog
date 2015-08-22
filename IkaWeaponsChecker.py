#!python
# -*- coding: utf-8 -*-

import numpy as np
import cv2
import sys

class IkaWeaponsChecker:
	def getWeaponName(self, target, is_debug=False):
		target_hsv = cv2.cvtColor(target, cv2.COLOR_BGR2HSV)
		target_optimized_hsv = IkaWeaponsChecker.removeBackground(target_hsv)
		target_bgr = cv2.cvtColor(target_optimized_hsv, cv2.COLOR_HSV2BGR)

		if is_debug:
			cv2.imshow('remove_background', target_bgr)

		min = sys.maxsize
		min_name = None
		for weapon in self.weapons.values():
			x = cv2.norm(weapon['image'], target_bgr, cv2.NORM_L2)
			if min > x:
				min = x
				min_name = weapon['name']
			if is_debug:
				print(weapon['name'], ':', x)

		return min_name

	@staticmethod
	def removeBackground(image, delta=5, s_max=196):
		base_h = image[0, 0, 0]
		min = base_h - delta
		max = base_h + delta
		result = image.copy()
		height, width = result.shape[:2]
		for h in range(height):
			for w in range(width):
				if result[h, w, 0] >= min and result[h, w, 0] <= max and result[h, w, 1] > s_max:
					result[h, w, 2] = 0
		return result

	def __init__(self, respack, langpack):
		weapons_names = respack['weapons']['main_weapons']

		self.weapons = {}
		for (category_name, weapons_names_in_category) in weapons_names.items():
			for weapons_name in weapons_names_in_category:
				image_bgra = cv2.resize(cv2.imread('masks/main_weapons/' + category_name + '/' + weapons_name + '.png', cv2.IMREAD_UNCHANGED), (46, 46))
				if image_bgra is None:
					continue

				height, width = image_bgra.shape[:2]
				image_bgr = np.empty((height, width, 3), dtype = np.uint8)
				for h in range(height):
					for w in range(width):
						image_bgr[h, w] = image_bgra[h, w, 0:3] if image_bgra[h, w, 3] != 0 else [0, 0, 0]

				name = langpack['weapons']['main_weapons'][category_name][weapons_name]
				self.weapons[weapons_name] = { 'category': category_name, 'name': name, 'image': image_bgr }

if __name__ == "__main__":
	import json
	json_file = open('resources/res.json', 'r', encoding = 'utf-8')
	respack = json.load(json_file)
	json_file.close
	json_file = open('resources/lang-ja.json', 'r', encoding = 'utf-8')
	langpack = json.load(json_file)
	json_file.close
	del json_file

	target = cv2.imread(sys.argv[1])
	checker = IkaWeaponsChecker(respack, langpack)
	name = checker.getWeaponName(target, True)

	print('---')
	print('result:', name)

	cv2.imshow('target', target)
	cv2.waitKey()