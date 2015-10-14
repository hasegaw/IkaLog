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
from ikalog.utils import *


class NumberRecoginizer(CharacterRecoginizer):

    def __new__(cls, *args, **kwargs):

        if not hasattr(cls, '__instance__'):
            cls.__instance__ = super(
                NumberRecoginizer, cls).__new__(cls, *args, **kwargs)

        return cls.__instance__

    def __init__(self):

        if hasattr(self, 'trained') and self.trained:
            return

        super(NumberRecoginizer, self).__init__()

        model_name = 'data/number.model'
        if os.path.isfile(model_name):
            self.load_model_from_file(model_name)
            self.train()
            return

        IkaUtils.dprint('Building number recoginization model.')
        # try to rebuild model
        data = [
            {'file': 'numbers2/num0_1.png', 'response': 0, },
            {'file': 'numbers2/num0_2.png', 'response': 0, },
            {'file': 'numbers2/num0_3.png', 'response': 0, },
            {'file': 'numbers2/num1_1.png', 'response': 1, },
            {'file': 'numbers2/num1_2.png', 'response': 1, },
            {'file': 'numbers2/num1_3.png', 'response': 1, },
            {'file': 'numbers2/num2_1.png', 'response': 2, },
            {'file': 'numbers2/num2_2.png', 'response': 2, },
            {'file': 'numbers2/num2_3.png', 'response': 2, },
            {'file': 'numbers2/num3_1.png', 'response': 3, },
            {'file': 'numbers2/num3_2.png', 'response': 3, },
            {'file': 'numbers2/num3_3.png', 'response': 3, },
            {'file': 'numbers2/num4_1.png', 'response': 4, },
            {'file': 'numbers2/num4_2.png', 'response': 4, },
            {'file': 'numbers2/num4_3.png', 'response': 4, },
            {'file': 'numbers2/num5_1.png', 'response': 5, },
            {'file': 'numbers2/num5_2.png', 'response': 5, },
            {'file': 'numbers2/num5_3.png', 'response': 5, },
            {'file': 'numbers2/num6_1.png', 'response': 6, },
            {'file': 'numbers2/num6_2.png', 'response': 6, },
            {'file': 'numbers2/num6_3.png', 'response': 6, },
            {'file': 'numbers2/num7_1.png', 'response': 7, },
            {'file': 'numbers2/num7_2.png', 'response': 7, },
            {'file': 'numbers2/num7_3.png', 'response': 7, },
            {'file': 'numbers2/num8_1.png', 'response': 8, },
            {'file': 'numbers2/num8_2.png', 'response': 8, },
            {'file': 'numbers2/num8_3.png', 'response': 8, },
            {'file': 'numbers2/num9_1.png', 'response': 9, },
            {'file': 'numbers2/num9_2.png', 'response': 9, },
            {'file': 'numbers2/num9_3.png', 'response': 9, },

            # bigger
            {'file': 'numbers2/num0_4.png', 'response': 0, },
            {'file': 'numbers2/num0_4.png', 'response': 0, },
            {'file': 'numbers2/num0_4.png', 'response': 0, },
            # { 'file': 'numbers2/num1_4.png', 'response': 1, },
            # { 'file': 'numbers2/num1_5.png', 'response': 1, },
            # { 'file': 'numbers2/num1_6.png', 'response': 1, },
            {'file': 'numbers2/num2_4.png', 'response': 2, },
            {'file': 'numbers2/num2_5.png', 'response': 2, },
            {'file': 'numbers2/num2_6.png', 'response': 2, },
            {'file': 'numbers2/num3_4.png', 'response': 3, },
            {'file': 'numbers2/num3_5.png', 'response': 3, },
            {'file': 'numbers2/num3_6.png', 'response': 3, },
            {'file': 'numbers2/num4_4.png', 'response': 4, },
            {'file': 'numbers2/num4_5.png', 'response': 4, },
            {'file': 'numbers2/num4_5.png', 'response': 4, },
            {'file': 'numbers2/num5_4.png', 'response': 5, },
            {'file': 'numbers2/num5_4.png', 'response': 5, },
            {'file': 'numbers2/num5_4.png', 'response': 5, },
            {'file': 'numbers2/num6_4.png', 'response': 6, },
            {'file': 'numbers2/num6_5.png', 'response': 6, },
            {'file': 'numbers2/num6_6.png', 'response': 6, },
            {'file': 'numbers2/num7_4.png', 'response': 7, },
            {'file': 'numbers2/num7_5.png', 'response': 7, },
            {'file': 'numbers2/num7_5.png', 'response': 7, },
            {'file': 'numbers2/num8_4.png', 'response': 8, },
            {'file': 'numbers2/num8_5.png', 'response': 8, },
            {'file': 'numbers2/num8_6.png', 'response': 8, },
            {'file': 'numbers2/num9_4.png', 'response': 9, },
            {'file': 'numbers2/num9_5.png', 'response': 9, },
            {'file': 'numbers2/num9_6.png', 'response': 9, },

            {'file': 'numbers2/slash_1.png', 'response': '/', },
            {'file': 'numbers2/slash_2.png', 'response': '/', },
            {'file': 'numbers2/slash_3.png', 'response': '/', },
            {'file': 'numbers2/dot_1.png', 'response': '.', },
            {'file': 'numbers2/dot_2.png', 'response': '.', },
            {'file': 'numbers2/dot_3.png', 'response': '.', },

        ]

        for d in data:
            d['img'] = cv2.imread(d['file'])
            self.add_sample(d['response'], d['img'])
        self.save_model_to_file(model_name)

        self.train()
