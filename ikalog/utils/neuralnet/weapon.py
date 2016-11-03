#!/usr/bin/env python3
# -*- coding: utf-8 -*-
#
#  IkaLog
#  ======
#  Copyright (C) 2016 Takeshi HASEGAWA
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

import pickle
import os

import cv2
import numpy as np
import time

from ikalog.utils import IkaUtils
from ikalog.utils.neuralnet.functions import relu, forward_mlp


class WeaponClassifier(object):

    def test_samples_from_directory(self, base_dir):
        self.test_results = {}
        for root, dirs, files in os.walk(base_dir):
            l = []
            for file in files:
                if file.endswith(".png"):
                    filename = os.path.join(root, file)
                    img = cv2.imread(filename)
                    answer, distance = self.predict(img)
                    if not (answer in self.test_results):
                        self.test_results[answer] = []

                    r = {'filename': filename, 'distance': distance}
                    self.test_results[answer].append(r)

    def dump_test_results_html(self, short=False):
        short = False
        for key in sorted(self.test_results):
            distances = []
            hidden = 0
            for e in self.test_results[key]:
                distances.append(e['distance'])
            var = np.var(distances)

            print("<h3>%s (%d) var=%d</h1>" %
                  (key, len(self.test_results[key]), var))

            for e in self.test_results[key]:
                if (not short) or (e['distance'] > var):
                    print("<!-- %s %s --><img src=%s>" %
                          (key, e['distance'], e['filename']))
                else:
                    hidden = hidden + 1

            if hidden > 0:
                print('<p>(%d samples hidden)</p>' % hidden)

    def __init__(self, model_file=None):
        pass

    def model_filename(self):
        return 'data/weapons.nn.data'

    def load_model_from_file(self, model_file=None):
        _model_filename = model_file or self.model_filename()

        f = open(_model_filename, 'rb')
        l = pickle.load(f)
        f.close()
        self._weapons_keys = l['weapons_keys']
        self._layers = l['layers']

        for layer in self._layers:
            activation_func = {'relu': relu}.get(layer.get('activation'))
            if activation_func:
                layer['activation'] = activation_func
        # print(self._weapons_keys)
        # print(self._layers)

    def image_to_feature(self, img_weapon):
        img_weapon_hsv = cv2.cvtColor(img_weapon, cv2.COLOR_BGR2HSV)
        img_weapon_hsv_f32 = np.asarray(img_weapon_hsv, dtype=np.float32)
        img_weapon_hsv_f32[:, :, 0] /= 32
        img_weapon_hsv_f32[:, :, 1] /= 128
        img_weapon_hsv_f32[:, :, 2] /= 128
        return np.reshape(img_weapon_hsv_f32, (1, -1))

    def predict(self, img_weapon):
        t1 = time.time()
        feat_weapon = self.image_to_feature(img_weapon)
        # print(feat_weapon.shape)

        y = forward_mlp(feat_weapon, self._layers)
        y_id = np.argmax(y, axis=1)

        # print(y)
        # print(y_id)
        # print(self._weapons_keys[y_id[0]])
        # print(self._weapons_keys.index('sshooter'))

        t2 = time.time()

        IkaUtils.dprint('%s: predict %s took %s seconds' % (self, self._weapons_keys[y_id[0]], t2-t1))

        return self._weapons_keys[y_id[0]], 0

if __name__ == '__main__':
    import sys
    obj = WeaponClassifier()
    obj.load_model_from_file()

    img = cv2.imread(sys.argv[1], 1)
    print(obj.predict(img)[0])
