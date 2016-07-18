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
#  This is a developtment tool to create a filtering mask from multiple images.
#  Usage:
#    ./tools/create_mask.py --input img1.png img2.png --output mask.png
#
#  TODO:
#    Support other filters in addition to MM_DARK.
#
import argparse
import cv2
import os.path
import sys

# Append the Ikalog root dir to sys.path to import IkaUtils.
sys.path.append(os.path.join(os.path.dirname(__file__), '..'))
from ikalog.utils import *

def get_args():
    parser = argparse.ArgumentParser()
    parser.add_argument('--input', type=str, nargs='*', required=True)
    parser.add_argument('--output', type=str, required=True)
    return vars(parser.parse_args())

if __name__ == '__main__':
    args = get_args()
    filenames = args['input']
    img_masks = []

    for filename in filenames:
        img = cv2.imread(filename, 1)
        img_mask = matcher.MM_DARK()(img)
        img_masks.append(img_mask)

    result = img_masks[0]
    for mask in img_masks[1:]:
        result = cv2.bitwise_and(result, mask)
    cv2.imwrite(args['output'], result)
