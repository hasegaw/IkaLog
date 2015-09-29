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
import numpy as np

from ikalog.utils.character_recoginizer import *


class udemae(character_recoginizer):

    def __init__(self):
        super().__init__()

        model_name = 'data/udemae.model'
        if os.path.isfile(model_name):
            self.loadModelFromFile(model_name)
            self.train()
            print('Loaded udemae recoginization model.')
            return

        print('Building udemae recoginization model.')
        data = [
            {'file': 'numbers2/a1.png', 'response': 'a'},
            {'file': 'numbers2/b1.png', 'response': 'b'},
            {'file': 'numbers2/c1.png', 'response': 'c'},
            {'file': 'numbers2/s1.png', 'response': 's'},
            {'file': 'numbers2/s2.png', 'response': 's'},
            {'file': 'numbers2/plus.png', 'response': '+'},
            {'file': 'numbers2/minus.png', 'response': '-'},
        ]

        for d in data:
            d['img'] = cv2.imread(d['file'])
            self.addSample(d['response'], d['img'])
            self.addSample(d['response'], d['img'])
            self.addSample(d['response'], d['img'])
        self.saveModelToFile(model_name)

        self.train()

if __name__ == "__main__":
    udemae()
