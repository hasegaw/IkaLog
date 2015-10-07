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
import os
import pickle


class IkaGlyphRecoginizer(object):
    # Models
    groups = []

    # Normalize the image. (for weapons)
    #
    # - Crop the image
    # - Apply Laplacian edge detector
    # - Convert to grayscale
    # - Apply image thresholding
    # - Apply contour finding process
    # - Draw filled contours
    # - Resize to 8x8 
    #
    # @param img    the source image
    # @return (img,out_img)  the result
    def normalize_weapon_image(self, img):
        h = img.shape[0]
        w = img.shape[1]
        img = img[2:h - 4, 10:w - 3]

        out_img = img.copy()
        h = img.shape[0]
        w = img.shape[1]

        laplacian_threshold = 60
        img_laplacian = cv2.Laplacian(out_img, cv2.CV_64F)
        img_laplacian_abs = cv2.convertScaleAbs(img_laplacian)
        img_laplacian_gray = cv2.cvtColor(img_laplacian_abs, cv2.COLOR_BGR2GRAY)
        ret, img_laplacian_mask = cv2.threshold(img_laplacian_gray,laplacian_threshold,255,0)
        img_contours, contours, hierarchy = cv2.findContours( img_laplacian_mask, cv2.RETR_CCOMP, cv2.CHAIN_APPROX_SIMPLE )
        out_img = np.zeros(( h, w, 3), np.uint8)
        cv2.drawContours( out_img, contours, -1, (255,255,255), cv2.FILLED ) 
        img_mask = out_img.copy()
        out_img = cv2.cvtColor(out_img, cv2.COLOR_BGR2GRAY)
        out_img = cv2.resize(out_img,(8,8))

        if False:
            cv2.imshow('orig', cv2.resize(img, (160,160)))
            cv2.imshow('laplacian_abs', cv2.resize(img_laplacian_abs, (160,160)))
            cv2.imshow('laplacian_gray', cv2.resize(img_laplacian_gray, (160,160)))
            cv2.imshow('contours', cv2.resize(img_contours, (160,160)))
            cv2.imshow('out', cv2.resize(out_img, (160,160)))
            cv2.moveWindow('orig',80,20)
            cv2.moveWindow('laplacian_abs',80,220)
            cv2.moveWindow('laplacian_gray',80,420)
            cv2.moveWindow('contours',80,620)
            cv2.moveWindow('out',80,820)
            ch = 0xFF & cv2.waitKey(1)
            if ch == ord('q'):
               sys.exit()
        return [
            out_img,
            img,
            img_mask
        ]

    # Analyze a image.
    #
    def analyze_image(self, img, blocks_x=3, blocks_y=3, debug=False):
        imgs = self.normalize_weapon_image(img)
        param = {'hist': imgs[0]}
        dimg = imgs[1]
        return param, dimg

    def show_learned_weapon_image(self, l, name='hoge', save=None):
        if len(l) != 0:
            new_h = l[0].shape[0] * len(l)
            new_w = l[0].shape[1]

            dest = cv2.resize(l[0], (new_w, new_h))
            dest.fill(0)
            y = 0
            for i in l:
                h = i.shape[0]
                dest[y:y + h] = i[0: h]
                y = y + h

            cv2.imshow(name, dest)
            if save:
                cv2.imwrite(save, dest)

    def name2id(self, name):
        try:
            return self.weapon_names.index(name)
        except:
            self.weapon_names.append(name)
        return self.weapon_names.index(name)

    def id2name(self, id):
        return self.weapon_names[id]

    def knn_reset(self):
        self.samples = None  # np.empty((0, 21 * 14))
        self.responses = []
        self.model = cv2.ml.KNearest_create()
        self.trained = False

    def match(self, img):
        if not self.trained:
            return None, None

        param, dimg = self.analyze_image(img, debug=True)
        sample = param['hist']
        sample_f = np.array(sample, np.float32).reshape((1, len(sample) * len(sample[0])))

        k = 3
        retval, results, neigh_resp, dists = self.model.findNearest(
            sample_f, k)

        id = int(results.ravel())
        name = self.id2name(id)
        return name, dists[0][0]

    def add_sample1(self, name, sample):
        id = self.name2id(name)
        print('sample_name %s id %d' % (name, id))
        sample_f = np.array(sample, np.float32).reshape((1, len(sample) * len(sample[0])))

        if self.samples is None:
            # すべてのデータは同じ次元であると仮定する
            self.samples = np.empty((0, len(sample) * len(sample[0])))
            self.responses = []
        # 追加
        self.samples = np.append(self.samples, sample_f, 0)
        self.responses.append(id)

    def knn_train_from_group(self):
        # 各グループからトレーニング対象を読み込む
        for group in self.groups:
            print('Group %s' % group['name'])
            for sample_tuple in group['learn_samples']:
                sample_data = sample_tuple[1]['hist']
                self.add_sample1(group['name'], sample_data)

    def knn_train(self):
        # 終わったら
        samples = np.array(self.samples, np.float32)
        responses = np.array(self.responses, np.float32)
        responses = responses.reshape((responses.size, 1))

        print('start model.train', len(responses))
        self.model.train(samples, cv2.ml.ROW_SAMPLE, responses)
        print('done model.train')
        self.trained = True

    def learn_image_group(self, name=None, dir=None):
        group_info = {
            'name': name,
            'images': [],
            'learn_samples': [],
        }

        l = []
        l_hist = []
        samples = []
        for root, dirs, files in os.walk(dir):
            for file in sorted(files):
                if file.endswith(".png"):
                    f = os.path.join(root, file)
                    img = cv2.imread(f)
                    samples.append(img)
                    param, dimg = self.analyze_image(img, debug=True)
                    sample_tuple = (img, param, dimg, f)
                    group_info['images'].append(sample_tuple)

#                    if len(group_info['images']) > 50:
#                        return

        # とりあえず最初のいくつかを学習
        for sample_tuple in group_info['images'][1:20]:
            group_info['learn_samples'].append(sample_tuple)

        print('  読み込み画像数', len(group_info['images']))
        self.groups.append(group_info)

        return group_info

    def save_model_to_file(self, file):
        f = open(file, 'wb')
        pickle.dump([self.samples, self.responses, self.weapon_names], f)
        f.close()

    def load_model_from_file(self, file):
        f = open(file, 'rb')
        l = pickle.load(f)
        f.close()
        self.samples = l[0]
        self.responses = l[1]
        self.weapon_names = l[2]

    def __init__(self):
        self.weapon_names = []
        self.knn_reset()
        self.groups = []
