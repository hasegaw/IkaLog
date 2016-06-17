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

    def pca_backproject_test(self, img):
        """
        Project, then backproject the image to test PCA ability.
        """
        if self._pca_dim is None:
            return img

        # Project
        features = np.array(self.extract_features(
            img), dtype=np.float32).reshape((1, -1))
        features = cv2.PCAProject(
            data=features,
            mean=self._pca_mean,
            eigenvectors=self._pca_eigenvectors,
        )
        features = np.array(features, dtype=np.float32).reshape((1, -1))

        # BackProject
        back_projected = cv2.PCABackProject(
            data=features,
            mean=self._pca_mean,
            eigenvectors=self._pca_eigenvectors,
        )

        return np.array(back_projected, dtype=np.uint8).reshape(img.shape)

    def offset_image(self, img, ox, oy):
        sx1 = max(-ox, 0)
        sy1 = max(-oy, 0)

        dx1 = max(ox, 0)
        dy1 = max(oy, 0)

        out_height, out_width = img.shape[0:2]

        w = min(out_width - dx1, out_width - sx1)
        h = min(out_height - dy1, out_height - sy1)

        new_frame = np.zeros((out_height, out_width, 3), np.uint8)
        new_frame[dy1:dy1 + h, dx1:dx1 + w] = img[sy1:sy1 + h, sx1:sx1 + w]
        return new_frame

    def predict_list(self, img_list, by_name=True):
        """
        Predict list of images.
        """
        X = None
        n = 0
        for img in img_list:
            features = np.array(self.extract_features(
                img), dtype=np.float32).reshape((1, -1))

            if self._pca_dim is not None:
                features = cv2.PCAProject(
                    data=features,
                    mean=self._pca_mean,
                    eigenvectors=self._pca_eigenvectors,
                )
                features = np.array(
                    features, dtype=np.float32).reshape((1, -1))

            if X is None:
                X = np.zeros(
                    (len(img_list), features.shape[1]), dtype=np.float32)
            X[n, :] = features
            n = n + 1

        retval, results, neigh_resp, dists = \
            self.model.findNearest(X, self._k)

        responses_int = np.array(results, dtype=np.int)
        if by_name:
            keys = list(
                map(lambda response: self.id2name(response), responses_int))
            return keys, dists

        return responses_int, dists

    def predict_slide(self, img):
        """
        Predict a image. Try finding the best fit by offsetting the image.
        """
        x_val_list = [-2, -1, 0, 1, 2]
        y_val_list = [-2, -1, 0, 1, 2]

        img_list = []
        for x in x_val_list:
            for y in x_val_list:
                img_list.append(self.offset_image(img, x, y))

        responses, dists = self.predict_list(img_list)
        dists2 = np.amin(dists, axis=1)
        best_index = np.argmin(np.array(dists2))
        return responses[best_index], dists[best_index]

    def predict(self, img):
        """
        Predict a image.
        """

        if not self.trained:
            return None, None

        keys, dists = self.predict_list([img])
        return keys[0], dists[0]

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

        if self._pca_dim is not None:
            print('Applying PCA....')
            self._pca_mean, self._pca_eigenvectors = cv2.PCACompute(
                data=self.samples,
                mean=None,
                maxComponents=self._pca_dim,
            )

            self.samples = cv2.PCAProject(
                data=self.samples,
                mean=self._pca_mean,
                eigenvectors=self._pca_eigenvectors,
            )

            # assert self._samples.shape[0] == self.responses.shape[0]
            assert self.samples.shape[1] == self._pca_dim
            print('PCA Done')
            print(self.samples.shape)

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
        for sample in group_info['images'][0:100]:
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
        pickle.dump([
            self.samples,
            self.responses,
            self.icon_names,
            self._pca_dim,
            self._pca_mean,
            self._pca_eigenvectors,
        ], f)
        f.close()

    def load_model_from_file(self, file):
        f = open(file, 'rb')
        l = pickle.load(f)
        f.close()
        self.samples = l[0]
        self.responses = l[1]
        self.icon_names = l[2]
        if len(l) >= 6:
            self._pca_dim = l[3]
            self._pca_mean = l[4]
            self._pca_eigenvectors = l[5]
        else:
            self._pca_dim = None

    def __init__(self, k=3, pca_dim=None):
        self.icon_names = []
        self.knn_reset()
        self.groups = []
        self._k = k
        self._pca_dim = pca_dim
        self._pca_mean = None
        self._pca_eigenvectors = None
