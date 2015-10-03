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
import numpy as np
import os
import pickle


class IkaGlyphRecoginizer(object):
    # Maximum Hue Value in OpenCV HSV Color.
    _HSV_COLOR_MAX = 185

    # Number of Hue samples
    _HSV_COLOR_SAMPLES = 36

    # Models
    groups = []

    # pre-calculated Hue samples

    def calcurate_hue_samples(self, num_colors):
        samples = []
        for i in range(num_colors):
            c_min = self._HSV_COLOR_MAX / num_colors * i
            c_max = self._HSV_COLOR_MAX / num_colors * (i + 1)
            if c_min == 0:
                c_min = 1
            samples.append((c_min, c_max))
        return samples

    # Normalize the image. (for weapons)
    #
    # - Crop the image
    # - Detect background color
    # - Replace the background color to black
    # - Replace white color to blue (0, 0, 255) because we want to compare using Hue value.
    #
    # @param img    the source image
    # @return (img,out_img)  the result
    def normalize_weapon_image(self, img):
        h = img.shape[0]
        w = img.shape[1]
        img = img[2:h - 4, 5:w - 3]

        out_img = img.copy()
        h = img.shape[0]
        w = img.shape[1]

        laplacian_threshold = 68

        img_laplacian = cv2.Laplacian(out_img, cv2.CV_64F)
        img_laplacian_abs = cv2.convertScaleAbs(img_laplacian)
        img_laplacian_gray = cv2.cvtColor(
            img_laplacian_abs, cv2.COLOR_BGR2GRAY)
        ret, img_laplacian_mask = cv2.threshold(
            img_laplacian_gray, laplacian_threshold, 255, 0)
        #out_img = cv2.bitwise_and(out_img, out_img, mask=img_laplacian_mask )
        img_contours, contours, hierarchy = cv2.findContours(
            img_laplacian_mask, cv2.RETR_CCOMP, cv2.CHAIN_APPROX_SIMPLE)
        cv2.drawContours(out_img, contours, -1, (0, 255, 0), cv2.FILLED)

        img_hsv = cv2.cvtColor(out_img, cv2.COLOR_BGR2HSV)

        bgcolor_sample = img_hsv[h - 3:h, 0:3, 0]  # Hue
        bg_h_color = np.average(bgcolor_sample)
        rad = 7
        bg_h_color1 = int(bg_h_color - rad)
        bg_h_color2 = int(bg_h_color + rad)

        img_mask = cv2.inRange(img_hsv[:, :, 0], bg_h_color1, bg_h_color2)
        img_mask2 = 255 - cv2.inRange(img_hsv[:, :, 2], 165, 255)  # Visibility
        img_mask = np.minimum(img_mask, img_mask2)

        # TODO: ブキの色（下の方）が明るいものはさらに抜く

        # 中間画像に対してマスクを適用
        for i in range(3):
            out_img[:, :, i] = np.minimum(out_img[:, :, i], 255 - img_mask)

        # デコ/カスタム要素で認識を優先するため画像で該当部分を拡大
        x1 = 0
        x2 = int(w * 0.7)
        y1 = h - 10
        out_img[y1: h - 1, x1:w - 1, :] = cv2.resize(
            out_img[y1: h - 1, x2: w - 1], (w - x1 - 1, h - y1 - 1), interpolation=cv2.INTER_NEAREST)
        img_hsv = cv2.cvtColor(out_img, cv2.COLOR_BGR2HSV)

        # 白いところを検出する (s が低く v が高い)
        white_mask_s = cv2.inRange(img_hsv[:, :, 1], 0, 48)
        white_mask_v = cv2.inRange(img_hsv[:, :, 2], 224, 256)
        white_mask = np.minimum(white_mask_s, white_mask_v)

        # 白色を置きかえ
        out_img[:, :, 0] = np.maximum(out_img[:, :, 0], white_mask)
        out_img[:, :, 1] = np.minimum(out_img[:, :, 1], 255 - white_mask)
        out_img[:, :, 2] = np.minimum(out_img[:, :, 2], 255 - white_mask)

        #cv2.imshow('orig', img)
        #cv2.imshow('H', img_h)
        #cv2.imshow('S', img_s)
        #cv2.imshow('V', img_v)
        #cv2.imshow('HSV', img_hsv)
        #cv2.imshow('mask', img_mask)
        #cv2.imshow('mask2', img_mask2)
        # cv2.waitKey()
        return [
            out_img,
            img,
        ]

    def count_h(self, img_h, samples):
        r = []
        for sample in samples:
            x = cv2.inRange(img_h, sample[0], sample[1])
            cond = x > 127
            r.append(len(np.extract(cond, img_h)))
        return r

    # Analyze a image.
    #
    def analyze_image(self, img, blocks_x=3, blocks_y=3, debug=False):
        samples = self._precalculated_hue_samples

        imgs = self.normalize_weapon_image(img)
        d = imgs[0]
        bw = int(d.shape[1] / blocks_x)
        bh = int(d.shape[0] / blocks_y)

        img_hsv = cv2.cvtColor(d, cv2.COLOR_BGR2HSV)
        img_h = img_hsv[:, :, 0]
        img_s = img_hsv[:, :, 1]
        img_v = img_hsv[:, :, 2]

        hist = []
        part_img_h = np.zeros((bh, bw), np.uint8)
        part_img_s = np.zeros((bh, bw), np.uint8)

        for bx in range(blocks_x):
            for by in range(blocks_y):
                x1 = bw * (bx + 0)
                x2 = bw * (bx + 1)
                y1 = bh * (by + 0)
                y2 = bh * (by + 1)
                part_img_h[:, :] = img_h[y1:y2, x1:x2]
                part_img_s[:, :] = img_s[y1:y2, x1:x2]
                hist.extend(self.count_h(part_img_h, samples))

        param = {'hist': np.array(hist).astype(dtype=np.float)}
        if (not debug):
            return param

        offset_w = 100  # img_h.shape[1]
        new_w = offset_w + (len(hist) * 8)
        new_h = img.shape[0]
        dimg = cv2.resize(img, (new_w, new_h))
        dimg.fill(0)
        dimg = cv2.cvtColor(dimg, cv2.COLOR_BGR2HSV)

        # カラーバーを書く
        for i in range(len(hist)):
            sample = samples[i % len(samples)]
            c_avg = int((sample[0] + sample[1]) / 2)

            y1 = new_h - hist[i]
            y2 = new_h
            x1 = offset_w + 8 * (i + 0)
            x2 = offset_w + 8 * (i + 1)

            dimg[:, x1:x2, 0].fill(c_avg)
            dimg[:, x1:x2, 1].fill(255)
            dimg[:, x1:x2, 2].fill(0)
            dimg[y1:y2, x1:x2, 2].fill(255)

        dimg = cv2.cvtColor(dimg, cv2.COLOR_HSV2BGR)
        w = imgs[0].shape[1]
        h = imgs[0].shape[0]
        dimg[:h, :w] = imgs[0][:, :]
        dimg[:h, w:w * 2] = imgs[1][:, :]
        # cv2.imshow(':D', dimg)
        # cv2.waitKey(3000)

        return param, dimg

    def calculate_parameters_from_samples(self, l_hist):
        num_samples = len(l_hist)
        colors = len(l_hist[0])

        a = np.array(l_hist).astype(dtype=np.float)
        # print("num_samples = %d, colors = %d" % (num_samples, colors))
        # print(a)
        # print(len(a[:,1]))

        b = a.T
        # print(len(b[:,1]))

        h_avg = np.average(b, axis=1)
        h_var = np.var(b, axis=1)
        from pprint import pprint
        # pprint(h_avg)
        # pprint(h_var)

        for e in a:
            abs_val = np.abs(e - h_avg)
            cond = (abs_val < h_var)
            # print(cond)

            n = len(np.extract(cond, cond))
            # print(n)

        return {'h_avg': h_avg, 'h_var': h_var}

    def show_learned_weapon_image(self, l, name='hoge', save=None):
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
        sample_f = np.array(sample, np.float32).reshape((1, len(sample)))

        k = 3
        retval, results, neigh_resp, dists = self.model.findNearest(
            sample_f, k)

        id = int(results.ravel())
        name = self.id2name(id)
        return name, dists[0][0]

    def add_sample1(self, name, sample):
        id = self.name2id(name)
        print('sample_name %s id %d' % (name, id))

        sample_f = np.array(sample).reshape((1, len(sample)))
        sample_f = np.array(sample_f, np.float32)

        if self.samples is None:
                # すべてのデータは同じ次元であると仮定する
            self.samples = np.empty((0, len(sample)))
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
        self._precalculated_hue_samples = self.calcurate_hue_samples(
            self._HSV_COLOR_SAMPLES)
        self.weapon_names = []
        self.knn_reset()
        self.groups = []
