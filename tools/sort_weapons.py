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

from ikalog.utils import WeaponRecoginizer

weapons = WeaponRecoginizer()
weapons.load_model_from_file()
weapons.knn_train()

results = {}
for root, dirs, files in os.walk(base_dir):
    l = []
    for file in files:
        if file.endswith(".png"):
            filename = os.path.join(root, file)
            img = cv2.imread(filename)
            answer, distance = weapons.match(img)
            if not (answer in results):
                results[answer] = []

            results[answer].append( { 'filename': filename, 'distance': distance } )

for weapon in sorted(results):
    print("<h3>%s (%d)</h1>" % (weapon, len(results[weapon])))

    for e in results[weapon]:
        print("<!-- %s %s --><img src=%s>" % (weapon, e['distance'], e['filename']))
