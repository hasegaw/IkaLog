#!/usr/bin/env python3
# -*- coding: utf-8 -*-
#
#  IkaLog
#  ======
#  Copyright (C) 2015- Takeshi HASEGAWA and IkaLog developers
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


class ImageClassifier(object):

    def __init__(self, rect=None, resize=None, num_classes=1, pca_components=None, labels=None):
        self._rect = rect
        self._resize = resize
        self._num_classes = num_classes
        self._labels = labels
        self._pca_components = pca_components
        self._pca_mean = None
        self._pca_eigenvectors = None
        pass

    """
    Persistency
    """

    def __getstate__(self):
        return {
            'rect': self._rect,
            'resize': self._resize,
            'num_classes': self._num_classes,
            'labels': self._labels,

            'train_x': self._x,
            'train_y': self._y,

            'pca_components': self._pca_components,
            'pca_mean': self._pca_mean,
            'pca_eigenvectors': self._pca_eigenvectors,
        }

    def __setstate__(self, state):
        self._rect = state.get('rect')
        self._resize = state.get('resize')
        self._labels = state.get('labels')
        self._num_classes = state.get('num_classes')
        self._x = state.get('train_x')
        self._y = state.get('train_y')
        self._pca_components = state.get('pca_components')
        self._pca_mean = state.get('pca_mean')
        self._pca_eigenvectors = state.get('pca_eigenvectors')

    def save_svm_to_file(self, filename):
        assert len(self._svm_dict) == self._num_classes

        for svm_obj in self._svm_dict:
            i = self._svm_dict.index(svm_obj)
            svm_filename = '%s.%d.svm' % (filename, i)
            print('%s.%d.svm' % (filename, i))
            svm_obj.save(svm_filename)

    def load_svm_from_file(self, filename):
        self._svm_dict = []

        for i in range(self._num_classes):
            svm_filename = '%s.%d.svm' % (filename, i)
            svm_obj = cv2.ml.SVM_load(svm_filename)
            assert svm_obj is not None, 'Failed to load ML data: %s' % filename
            self._svm_dict.append(svm_obj)

    def save_to_file(self, filename):
        f = open('%s.pickle.dat' % filename, 'wb')
        pickle.dump(self.__getstate__(), f)
        f.close()
        self.save_svm_to_file(filename)

    def load_from_file(self, filename):
        f = open('%s.pickle.dat' % filename, 'rb')
        state = pickle.load(f)
        f.close()
        self.__setstate__(state)
        self.load_svm_from_file(filename)

        # self.retrain()

    """
    """

    def extract_rect(self, frame):
        if self._rect is None:
            raise Exception('no rect defiend')

        x1, y1, x2, y2 = self._rect
        return frame[y1:y2, x1:x2]

    """
    Training
    """

    def add_dataset_image(self, frame, label):

        if self._rect is not None:
            img_rect = self.extract_rect(frame)
        else:
            img_rect = frame

        if self._resize is not None:
            img_rect = cv2.resize(img_rect, self._resize)
        else:
            pass

        if 0:
            cv2.imshow('img_rect', img_rect)
            cv2.waitKey(1)
        f = self.rect_to_feature(img_rect)
        # f = cv2.resize(f, (32, 8))
#            f = cv2.cvtColor(f, cv2.COLOR_BGR2GRAY)
        f[f > 230] = 255
#            f[f < 200] = 0
#            f[f > 1] = 255
        num_samples_ = 15  # FIXME
        one_hot_vector = np.ones((num_samples_), dtype=np.int32) * -1

        if self._labels is None:
            one_hot_vector[label] = 1
        elif label != -1:
            one_hot_vector[self._labels.index(label)] = 1

        l = []
        l.append({'image': f, 'label': label, 'one_hot_vector': one_hot_vector})
        return l

    def get_train_dataset_image(self, img_filename, label):
        print(img_filename)
        img = cv2.imread(img_filename, 1)
        assert img is not None

        return self.add_dataset_image(img, label)

    def get_train_dataset_video(self, video_filename, label):
        print(video_filename)
        cap = cv2.VideoCapture(video_filename)

        l = []
        while (cap.isOpened()):
            ret, frame = cap.read()
            if frame is None:
                break
            ret, frame = cap.read()
            if frame is None:
                break
            ret, frame = cap.read()
            if frame is None:
                break

            l.extend(self.add_dataset_image(frame, label))
        return l

    def get_train_dataset1(self, filename, label):
        basename, ext = os.path.splitext(filename)
        if ext.lower() in ('.mp4', '.mov'):
            return self.get_train_dataset_video(filename, label)
        elif ext.lower() in ('.png', '.jpeg', '.jpg', '.bmp'):
            return self.get_train_dataset_image(filename, label)
        raise Exception('unknown format')

    """
    feature generation - WIP
    """

    def ft_image_transform(self, f):
        return f

    def ft_pca_transform(self, f):
        if (self._pca_components is not None):
            return cv2.PCAProject(f,  self._pca_mean, self._pca_eigenvectors)
        return f

    def rect_to_feature(self, img_rect, pca_transform=True):
        f = self.ft_image_transform(img_rect)
        if 0:
            f = self.ft_pca_transform(f)

        f = np.array(f, dtype=np.float32).reshape((1, -1))
        return f

    def post_filter(self, f):
        return f

    def pca_compute(self, data):
        assert self._pca_components > 0

        self._pca_mean, self._pca_eigenvectors = cv2.PCACompute(
            data=data,
            mean=np.mean(data, axis=0).reshape(1, -1),
            maxComponents=self._pca_components)
        print(self._pca_mean)
        print(self._pca_eigenvectors)

    """
    Training
    """

    def retrain(self, verbose=False):
        self._svm_dict = []

        for i in range(self._num_classes):
            if verbose:
                print("i = %d" % i)
            svm = cv2.ml.SVM_create()
            self._svm_dict.append(svm)
            svm.setType(cv2.ml.SVM_C_SVC)
            svm.setKernel(cv2.ml.SVM_LINEAR)

            svm_response = list(
                map(lambda d: {True: 1, False: -1}.get(d == i), self._y))
            svm_response_np = np.array(svm_response, dtype=np.int32)
            if verbose:
                print(svm_response)

            svm.setTermCriteria((cv2.TERM_CRITERIA_COUNT, 100, 1.e-06))
            svm.train(self._x, cv2.ml.ROW_SAMPLE, svm_response_np)
        if verbose:
            print("Training done")

    def train(self, x, y):
        self._x = np.array(x, dtype=np.float32)
        self._y = np.array(y, dtype=np.int32)
        self.retrain()

    def drop_train_data(self):
        self._x, self._y = None, None

    """
    Predict
    """

    def predict_vector(self, x_list):
        X_list = []

        for x in x_list:
            # x is a image.
            #x_f = self.rect_to_feature(x)
            x_f = x
            X = np.array(x_f, dtype=np.float32).reshape(1, -1)
            X_list.append(X[0])

        X_list = np.array(X_list, dtype=np.float32)
        # print(X_list.shape)

        if self._pca_components is not None:
            X = cv2.PCAProject(X, self._mean, self._eigenvectors)

        Y = np.zeros((len(self._svm_dict), X_list.shape[0]), dtype=np.int32)

        for i in range(len(self._svm_dict)):
            retval, y = self._svm_dict[i].predict(X_list)
            assert retval == 0.0
            Y[i, :] = y.reshape(-1)
        return Y.T

    def predict_index(self, x_list):
        y_vector = self.predict_vector(x_list)
        y_one_hot_vector = np.array(
            (y_vector + 1) / 2, dtype=np.int32)  # -1/1 to 0/1
        y_confusion = np.sum(y_one_hot_vector, axis=1)
        y = np.argmax(y_one_hot_vector, axis=1)
        y[y_confusion != 1] = -1
        return y

    def predict(self, x_list):
        y_index = self.predict_index(x_list)

        if self._labels is None:
            return y_index

        def convert_func(y): return (-1 if y == -1 else self._labels[y])
        return list(map(convert_func, y_index))

    def predict1(self, x):
        return self.predict([x])[0]

    def predict1_index(self, x):
        return self.predict_index([x])[0]

    def predict_frame(self, img):
        img_rect = self.extract_rect(img)
        return self.predict1(img_rect)


class unsupported(object):
    def predict(self, x):
        retval, y = self._svm_dict[1].predict(x)
        return y

    def predict1(self, x):
        # x should be BGR or gray image.
        assert len(x.shape) == 2 or (len(x.shape) == 3 and x.shape[2] == 3)

        """
        ToDo: 画像処理
        """
        f = self.rect_to_feature(x)

        X = np.array(f, dtype=np.float32).reshape(1, -1)
        if self._pca_components is not None:
            X = cv2.PCAProject(X, self._mean, self._eigenvectors)
        retval, y = self._svm_dict[0].predict(X)
        return y[0] == 1

    def predict1_multiclass_core(self, x):
        # x should be BGR or gray image.
        assert len(x.shape) == 2 or (len(x.shape) == 3 and x.shape[2] == 3)

        """
        ToDo: 画像処理
        """
        f = self.rect_to_feature(x)

        X = np.array(f, dtype=np.float32).reshape(1, -1)
        if self._pca_components is not None:
            X = cv2.PCAProject(X, self._mean, self._eigenvectors)
        r = []
        for k in range(len(self._svm_dict)):
            if (k == 0) or (k == None):
                next
            retval, y = self._svm_dict[k].predict(X)
            yy = (y + 1) / 2
            r.append(yy)
        return np.array(r, dtype=np.int32)

    def predict1_multiclass(self, x):
        y_one_hot_vector = self.predict1_multiclass_core(x)
        y_confusion = np.sum(y_one_hot_vector, axis=0)
        y = np.argmax(y_one_hot_vector, axis=0)
        y[y_confusion != 1] = -1
        return y

    def predict_frame(self, frame):
        return self.predict1(self.extract_rect(frame))
