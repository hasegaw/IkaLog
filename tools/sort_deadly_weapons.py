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

base_dir = sys.argv[1]

from ikalog.utils.character_recoginizer import DeadlyWeaponRecoginizer

recoginizer = DeadlyWeaponRecoginizer()

results = {}
for root, dirs, files in os.walk(base_dir):
    l = []
    for file in files:
        if file.endswith(".png"):
            filename = os.path.join(root, file)
            img = cv2.imread(filename)
            answer = recoginizer.match(img)
            if not (answer in results):
                results[answer] = []
            distance = 0
            results[answer].append( { 'filename': filename, 'distance': distance } )

for reason in sorted(results):
    print("<h3>%s (%d)</h1>" % (reason, len(results[reason])))

    for e in results[reason]:
        print("<!-- %s %s --><img src=\"%s\">" % (reason, e['distance'], e['filename']))
