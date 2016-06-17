#!/usr/bin/env python3
# -*- coding: utf-8 -*-
#
#  IkaLog
#  ======
#  Copyright (C) 2015 Takeshi HASEGAWA
#  Copyright (C) 2015 Hiromochi Itoh
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
import numpy as np

from ikalog.utils.icon_recoginizer import IconRecoginizer


class GearRecoginizer(IconRecoginizer):

    def extract_features_func(self, img, debug=False):
        img_resized = cv2.resize(img, (48,48))
        img_resized_hsv = cv2.cvtColor(img_resized, cv2.COLOR_BGR2HSV)
        features = img_resized_hsv.reshape(-1)
        return features

    def model_filename(self):
        return self._model_filename

    def load_model_from_file(self, model_file=None):
        if model_file is None:
            model_file = self.model_filename()

        super(GearRecoginizer, self).load_model_from_file(model_file)

    def save_model_to_file(self, model_file=None):
        if model_file is None:
            model_file = self.model_filename()

        super(GearRecoginizer, self).save_model_to_file(model_file)

    def __init__(self, model_filename):
        self._model_filename=model_filename
        super(GearRecoginizer, self).__init__(k=1, pca_dim=50)
