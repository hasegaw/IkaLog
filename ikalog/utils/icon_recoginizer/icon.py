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

import os
import pickle

import cv2
import numpy as np


class IconRecoginizer(object):

    def down_sample_2d(self, src, w, h):
        sy, sx = src.shape[0:2]

        out_img = np.zeros((h, w), np.uint8)
        for x in range(w):
            for y in range(h):
                x1 = int((x / w) * sx)
                y1 = int((y / h) * sy)
                x2 = int(((x + 1) / w) * sx)
                y2 = int(((y + 1) / h) * sy)
                out_img[y, x] = np.amax(src[y1:y2, x1:x2])

        max_value = np.amax(out_img)
        if max_value > 0:
            out_img = ((out_img * 1.0) / max_value)

        if 0:
            cv2.imshow('orig', cv2.resize(src, (128, 128),
                                          interpolation=cv2.INTER_NEAREST))
            cv2.imshow('resize', cv2.resize(
                out_img, (128, 128), interpolation=cv2.INTER_NEAREST))
            cv2.waitKey(10)

        return out_img

    # Normalize the image.
    #
    # - Crop the image
    # - Apply Laplacian edge detector
    # - Convert to grayscale
    # - Threshold the image
    # - Down-sample to 12x12
    #
    # @param img    the source image
    # @return (img,out_img)  the result
    def normalize_icon_image(self, img):
        h, w = img.shape[0:2]

        laplacian_threshold = 60
        img_laplacian = cv2.Laplacian(img, cv2.CV_64F)
        img_laplacian_abs = cv2.convertScaleAbs(img_laplacian)
        img_laplacian_gray = \
            cv2.cvtColor(img_laplacian_abs, cv2.COLOR_BGR2GRAY)
        ret, img_laplacian_mask = \
            cv2.threshold(img_laplacian_gray, laplacian_threshold, 255, 0)
        out_img = self.down_sample_2d(img_laplacian_mask, 12, 12)

        if False:
            cv2.imshow('orig', cv2.resize(img, (160, 160)))
            cv2.imshow('laplacian_abs', cv2.resize(
                img_laplacian_abs, (160, 160)))
            cv2.imshow('laplacian_gray', cv2.resize(
                img_laplacian_gray, (160, 160)))
            cv2.imshow('out', cv2.resize(out_img, (160, 160)))
            cv2.moveWindow('orig', 80, 20)
            cv2.moveWindow('laplacian_abs', 80, 220)
            cv2.moveWindow('laplacian_gray', 80, 420)
            cv2.moveWindow('out', 80, 820)
            ch = 0xFF & cv2.waitKey(1)
            if ch == ord('q'):
                sys.exit()
        return [
            out_img,
            img,
            img,  # ununsed
        ]

    # Define feature extraction algorithm.
    def extract_features_func(self, img, debug=False):
        return np.array(self.normalize_icon_image(img)[0])

    # Extract features
    def extract_features(self, img, debug=True):
        features = self.extract_features_func(img)

        if len(features.shape) > 1:
            features = features.reshape((1, -1))
        return features

    def show_learned_icon_image(self, l, name='hoge', save=None):
        if len(l) != 0:
            max_h = max(l, key=(lambda x: x.shape[0])).shape[0]
            new_h = max_h * len(l)
            new_w = max(l, key=(lambda x: x.shape[1])).shape[1]

            dest = cv2.resize(l[0], (new_w, new_h))
            dest.fill(0)
            y = 0
            for i in l:
                h = i.shape[0]
                dest[y:y + h] = i[0: h]
                y = y + max_h

            cv2.imshow(name, dest)
            if save:
                cv2.imwrite(save, dest)

    # index <-> id conversion

    def name2id(self, name):
        try:
            return self.icon_names.index(name)
        except ValueError:
            self.icon_names.append(name)

        return self.icon_names.index(name)

    def id2name(self, id):
        return self.icon_names[id]

    def knn_reset(self):
        self.samples = None  # np.empty((0, 21 * 14))
        self.responses = []
        self.model = cv2.ml.KNearest_create()
        self.trained = False

    def predict(self, img):
        if not self.trained:
            return None, None

        features = np.array(self.extract_features(img), dtype=np.float32)
        retval, results, neigh_resp, dists = \
            self.model.findNearest(features.reshape((1, -1)), self._k)

        id = int(results.ravel())
        name = self.id2name(id)
        return name, dists[0][0]

    def add_sample1(self, name, features):
        id = self.name2id(name)

        if self.samples is None:
            # すべてのデータは同じ次元であると仮定する
            dims = features.reshape((-1)).shape[0]
            self.samples = np.empty((0, dims))
            self.responses = []

        self.samples = np.append(self.samples, features.reshape((1, -1)), 0)
        self.responses.append(id)

    def knn_train_from_group(self):
        # 各グループからトレーニング対象を読み込む
        for group in self.groups:
            print('Group %s' % group['name'])
            for sample in group['learn_samples']:
                self.add_sample1(group['name'], sample['features'])

    def knn_train(self):
        # 終わったら
        samples = np.array(self.samples, np.float32)
        responses = np.array(self.responses, np.float32)
        responses = responses.reshape((responses.size, 1))

        self.model.train(samples, cv2.ml.ROW_SAMPLE, responses)
        print('%s: KNN Trained (%d samples)' %
              (self, len(responses)))
        self.trained = True

    def learn_image_group(self, name=None, dir=None):
        group_info = {
            'name': name,
            'images': [],
            'learn_samples': [],
        }

        l = []
        samples = []
        for root, dirs, files in os.walk(dir):
            for file in sorted(files):
                if file.endswith(".png"):
                    f = os.path.join(root, file)
                    img = cv2.imread(f)
                    samples.append(img)
                    features = self.extract_features(img)
                    sample = {'img': img, 'features': features, 'src_path': f}
                    group_info['images'].append(sample)

#                    if len(group_info['images']) > 50:
#                        return

        # とりあえず最初のいくつかを学習
        for sample in group_info['images'][1:100]:
            group_info['learn_samples'].append(sample)

        print('  読み込み画像数', len(group_info['images']))
        self.groups.append(group_info)

        return group_info

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

    def save_model_to_file(self, file):
        f = open(file, 'wb')
        pickle.dump([self.samples, self.responses, self.icon_names], f)
        f.close()

    def load_model_from_file(self, file):
        f = open(file, 'rb')
        l = pickle.load(f)
        f.close()
        self.samples = l[0]
        self.responses = l[1]
        self.icon_names = l[2]

    def __init__(self, k=3):
        self.icon_names = []
        self.knn_reset()
        self.groups = []
        self._k = k
