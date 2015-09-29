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
import os
import sys

sys.path.append('.')
base_dir = sys.argv[1]

from ikalog.utils import IkaGlyphRecoginizer

weapons = IkaGlyphRecoginizer()
weapons.load_model_from_file("data/weapons.trained")

for root, dirs, files in os.walk(base_dir):
    l = []
    results = {}
    for file in files:
        if file.endswith(".png"):
            f = os.path.join(root, file)
            img = cv2.imread(f)
            r, model = weapons.guessImage(img)
            #print("<br> %s %d<img src=%s>" % (r['name'], r['score'], f))
            name = r['name']
            if not name in results:
                results[name] = []

            results[name].append( { 'img': f, 'score': r['score'] } )

for weapon in weapons.models:
    name = weapon['name']
    if not name in results:
        count = 0
    else:
        count = len(results[name])
    print("<h3>%s (%d)</h1>" % (name, count))
    if count == 0:
        continue
    for e in results[name]:
        print("<!-- %d --><img src=%s>" % (e['score'], e['img']))
