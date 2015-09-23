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
import numpy as np
import cv2
import sys
import traceback
from datetime import datetime
from IkaGlyphRecoginizer import *
from IkaUtils import *


class IkaKdRecoginizer:

    samples = np.empty((0, 21 * 14))
    responses = []
    model = cv2.ml.KNearest_create()

    def saveModelToFile(self, file):
        f = open(file, "wb")
        pickle.dump([self.samples, self.responses], f)
        f.close()

    def loadModelFromFile(self, file):
        f = open(file, "rb")
        l = pickle.load(f)
        f.close()
        self.samples = l[0]
        self.responses = l[1]
        # print(self.samples.shape)
        # print(self.responses)

    def preprocess(self, img):
        img = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
        ret, img = cv2.threshold(img, 230, 255, cv2.THRESH_BINARY)
        return img

    def teach(self, file):
        img = cv2.imread(file, 1)
        img = self.preprocess(img)
        img1 = img[:, 0:14]
        img2 = img[:, 15:29]
        print(img1.shape, img2.shape)
        cv2.imshow('what is this number?', img2)

        key = cv2.waitKey()
        sys.stdout.write('%d' % (key - 48))

        sample = img2.reshape((1, img2.shape[0] * img2.shape[1]))

        self.samples = np.append(self.samples, sample, 0)
        self.responses.append(key - 48)

    def matchSingleDigit(self, img):
        raito = np.sum(
            img) / (img.shape[0] * img.shape[1]) if np.sum(img) != 0 else 0.0

        if raito < 0.1:
            # ほぼ真っ黒
            return 0

        sample = img.reshape((1, img.shape[0] * img.shape[1]))
        sample = np.array(sample, np.float32)

        k = 3

        retval, results, neigh_resp, dists = self.model.findNearest(sample, k)

        d = int(results.ravel())
        return d

    def match(self, img):
        if not self.trained:
            return None

        img = self.preprocess(img)
        img1 = img[:, 0:14]
        img2 = img[:, 15:29]

        num = self.matchSingleDigit(img1) * 10 + self.matchSingleDigit(img2)
        return num

    def train(self):
        samples = np.array(self.samples, np.float32)
        responses = np.array(self.responses, np.float32)
        responses = responses.reshape((responses.size, 1))
        responses = np.array(self.responses, np.float32)
        self.model.train(samples, cv2.ml.ROW_SAMPLE, responses)
        self.trained = True

    def __init__(self):
        self.trained = False


class IkaUdemaeRecoginizer:

    udemae_matchers = []

    def match(self, img):
        img_gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
        ret, img_threshold = cv2.threshold(
            img_gray, 230, 255, cv2.THRESH_BINARY)

        for matcher in self.udemae_matchers:
            if matcher.match(img_threshold):
                return matcher.label
        return None

    def loadUdemaeMask(self, debug=False):
        self.udemae_matchers = []
        udemae_list = [
            {'file': 'udemae_c1.png', 'text': 'C-', },
            {'file': 'udemae_c2.png', 'text': 'C', },
            {'file': 'udemae_c3.png', 'text': 'C+', },
            {'file': 'udemae_b1.png', 'text': 'B-', },
            {'file': 'udemae_b2.png', 'text': 'B', },
            {'file': 'udemae_b3.png', 'text': 'B+', },
            {'file': 'udemae_a1.png', 'text': 'A-', },
            {'file': 'udemae_a2.png', 'text': 'A', },
            {'file': 'udemae_a3.png', 'text': 'A+', },
            # {'file': 'udemae_s1.png', 'text': 'S-', },
            {'file': 'udemae_s2.png', 'text': 'S', },
            {'file': 'udemae_s3.png', 'text': 'S+', },
        ]
        for udemae in udemae_list:
            mask_filename = os.path.join('masks', udemae['file'])
            matcher = IkaMatcher(
                0, 0, 115, 45,
                img_file=mask_filename,
                threshold=0.99,
                orig_threshold=0.01,
                false_positive_method=IkaMatcher.FP_BACK_IS_BLACK,
                pre_threshold_value=230,
                label=udemae['text'],
                debug=debug,
            )
            self.udemae_matchers.append(matcher)


class IkaScene_ResultDetail:

    def isEntryMe(self, entry_img):
        # ヒストグラムから、入力エントリが自分かを判断
        if len(entry_img.shape) > 2 and entry_img.shape[2] != 1:
            me_img = cv2.cvtColor(entry_img[:, 0:43], cv2.COLOR_BGR2GRAY)
        else:
            me_img = entry_img[:, 0:43]

        ret, me_img = cv2.threshold(me_img, 230, 255, cv2.THRESH_BINARY)

        me_score = np.sum(me_img)
        me_score_normalized = 0
        try:
            me_score_normalized = me_score / (43 * 45 * 255 / 10)
        except ZeroDivisionError as e:
            me_score_normalized = 0

        #print("score=%3.3f" % me_score_normalized)

        return (me_score_normalized > 1)

    _n = 0
    rank_imgs = {}

    plot_img = np.zeros((2000, 1000, 1), np.uint8)
    plot_img2 = np.zeros((2000, 1000, 1), np.uint8)

    def guessFesTitle(self, img_fes_title):
        img_fes_title_hsv = cv2.cvtColor(img_fes_title, cv2.COLOR_BGR2HSV)
        yellow = cv2.inRange(img_fes_title_hsv[:, :, 0], 32 - 2, 32 + 2)
        yellow2 = cv2.inRange(img_fes_title_hsv[:, :, 2], 240, 255)
        img_fes_title_mask = np.minimum(yellow, yellow2)
        is_fes = np.sum(img_fes_title_mask) > img_fes_title_mask.shape[
            0] * img_fes_title_mask.shape[1] * 16

        # 文字と判断したところを 1 にして縦に足し算

        img_fes_title_hist = np.sum(
            img_fes_title_mask / 255, axis=0)  # 列毎の検出dot数
        a = np.array(range(len(img_fes_title_hist)), dtype=np.int32)
        b = np.extract(img_fes_title_hist > 0, a)
        x1 = np.amin(b)
        x2 = np.amax(b)

        # 最小枠で crop
        img_fes_title_new = img_fes_title[:, x1:x2]

        # ボーイ/ガールは経験上横幅 56 ドット
        gender_x1 = x2 - 36
        gender_x2 = x2
        img_gender = img_fes_title_mask[:, gender_x1:gender_x2]

        x_center = int(img_gender.shape[1] / 2)
        y_center = int(img_gender.shape[0] * 0.6)

        score1 = np.sum(img_gender[:y_center, :x_center] / 255)
        score2 = np.sum(img_gender[:y_center, x_center:] / 255)
        score3 = score1 / score2

        score1 = np.sum(img_gender[y_center:, :x_center] / 255)
        score2 = np.sum(img_gender[y_center:, x_center:] / 255)
        score4 = score1 / score2

        #print("%d, %d " % (score1, score2))
        #print("%f,%f" % (score3, score4))

        x = score3 * 100
        y = score4 * 100

        #self.plot_img[y:y + img_gender.shape[0], x:x + img_gender.shape[1], 0] = img_gender

#		cv2.imshow('fes_gender', img_gender)
#		cv2.waitKey()

        # ふつうの/まことの/スーパー/カリスマ/えいえん
        img_fes_rank = img_fes_title_mask[:, 0:52]
        # 4ブロックで処理
        blocks = 6
        block_w = img_fes_rank.shape[1] / blocks
        y_center = int(img_fes_rank.shape[0] * 0.4)
        scores = []
        for i in range(blocks):
            rank_x1 = x1 + block_w * i
            rank_x2 = x1 + block_w * (i + 1)
            score = np.sum(img_fes_rank[:y_center, rank_x1:rank_x2] / 255)
            scores.append(score)
            score = np.sum(img_fes_rank[y_center:, rank_x1:rank_x2] / 255)
            scores.append(score)

        norm = scores[1]

        norm_scores = []
        for i in range(len(scores)):
            norm_scores.append(scores[i] / norm)

        x = int(scores[7] / norm * 300)
        y = int(scores[3] / norm * 300)
        print("normalised_scores = %s", norm_scores)
        x2 = img_fes_rank.shape[1] + x
        y2 = img_fes_rank.shape[0] + y

        cond1 = scores[0] / norm > 0.75  # カリスマ、スーパー |
        cond2 = scores[6] / norm > 0.75  # カリスマ
        cond3 = scores[3] / norm > 0.75  # ふつうの
        cond7 = scores[7] / norm > 0.75  # まことの or えいえんの

        cond = cond7

        prefix = None
        if cond2:
            prefix = "カリスマ"

        if (not prefix) and cond1 and (not cond2):
            prefix = "スーパー"

        if (not prefix) and cond3:
            prefix = "ふつうの"

        if (not prefix) and cond7:
            prefix = "まことの"

        if (not prefix):
            prefix = "えいえんの"

        if (not prefix):
            if cond:
                self.plot_img2[y:y2, x:x2, 0] = 255 - img_fes_rank
            else:
                self.plot_img2[y:y2, x:x2, 0] = img_fes_rank

        # まだわからないものだけ
        if (not prefix):
            for i in range(len(scores)):
                x = i * img_fes_rank.shape[1] * 1.3
                y = int(scores[i] / norm * 300)
                x2 = img_fes_rank.shape[1] + x
                y2 = img_fes_rank.shape[0] + y
                print(x, y, x2, y2)
                self.plot_img[y:y2, x:x2, 0] = img_fes_rank

        if (not prefix):
            prefix = "others"

        if prefix:
            if not prefix in self.rank_imgs:
                self.rank_imgs[prefix] = []
            self.rank_imgs[prefix].append(img_fes_rank)

#		cv2.imshow('plot_all_values', self.plot_img)
#		cv2.imshow('plot_xy', self.plot_img2)
#		cv2.imshow('fes_rank', img_fes_rank)
#		cv2.waitKey()

        if (score4 < 1.1):
            gender = "ガール"
        else:
            gender = "ボーイ"

        self._n = self._n + 1
        cv2.imwrite('_fes_title.%d.png' % self._n, img_fes_title_new)

        return {'img_fes_title_new': img_fes_title_new, 'gender': gender, 'prefix': prefix}

    def analyzeEntry(self, img_entry):
        # 各プレイヤー情報のスタート左位置
        entry_left = 610
        # 各プレイヤー報の横幅
        entry_width = 610
        # 各プレイヤー情報の高さ
        entry_height = 46

        # 各エントリ内での名前スタート位置と長さ
        entry_xoffset_weapon = 760 - entry_left
        entry_xoffset_weapon_me = 719 - entry_left
        entry_width_weapon = 47

        entry_xoffset_name = 809 - entry_left
        entry_xoffset_name_me = 770 - entry_left
        entry_width_name = 180

        entry_xoffset_nawabari_score = 995 - entry_left
        entry_width_nawabari_score = 115

        entry_xoffset_kd = 1185 - entry_left
        entry_width_kd = 31
        entry_height_kd = 21

        me = self.isEntryMe(img_entry)
        if me:
            weapon_left = entry_xoffset_weapon_me
            name_left = entry_xoffset_name_me
            rank_left = 0
        else:
            weapon_left = entry_xoffset_weapon
            name_left = entry_xoffset_name
            rank_left = 43

        img_rank = img_entry[20:45, rank_left:rank_left + 43]
        img_weapon = img_entry[:, weapon_left:weapon_left + entry_width_weapon]
        img_name = img_entry[:, name_left:name_left + entry_width_name]
        img_score = img_entry[
            :, entry_xoffset_nawabari_score:entry_xoffset_nawabari_score + entry_width_nawabari_score]
        img_kills = img_entry[0:entry_height_kd,
                              entry_xoffset_kd:entry_xoffset_kd + entry_width_kd]
        img_deaths = img_entry[entry_height_kd:entry_height_kd *
                               2, entry_xoffset_kd:entry_xoffset_kd + entry_width_kd]

        img_fes_title = img_name[0:entry_height / 2, :]
        img_fes_title_hsv = cv2.cvtColor(img_fes_title, cv2.COLOR_BGR2HSV)
        yellow = cv2.inRange(img_fes_title_hsv[:, :, 0], 32 - 2, 32 + 2)
        yellow2 = cv2.inRange(img_fes_title_hsv[:, :, 2], 240, 255)
        img_fes_title_mask = np.minimum(yellow, yellow2)
        is_fes = np.sum(img_fes_title_mask) > img_fes_title_mask.shape[
            0] * img_fes_title_mask.shape[1] * 16
        if is_fes:
            fes_info = self.guessFesTitle(img_fes_title)

        entry = {
            "me": me,
            "img_rank": img_rank,
            "img_weapon": img_weapon,
            "img_name": img_name,
            "img_score": img_score,
            "img_kills": img_kills,
            "img_deaths": img_deaths,
        }

        if is_fes:
            entry["img_fes_title"] = img_fes_title
            entry["gender"] = fes_info["gender"]
            entry["prefix"] = fes_info["prefix"]

        if self.udemae_recoginizer:
            try:
                # Udemae will be shown in img_score in ranked battles.
                udemae = self.udemae_recoginizer.match(entry['img_score'])
                if udemae:
                    entry['udemae_pre'] = udemae
            except:
                IkaUtils.dprint('Exception occured in Udemae recoginization.')
                IkaUtils.dprint(traceback.format_exc())

        if self.kd_recoginizer:
            try:
                entry['kills'] = self.kd_recoginizer.match(entry['img_kills'])
                entry['deaths'] = self.kd_recoginizer.match(
                    entry['img_deaths'])

            except:
                IkaUtils.dprint('Exception occured in K/D recoginization.')
                IkaUtils.dprint(traceback.format_exc())

            try:
                result, model = self.weapons.guessImage(entry['img_weapon'])
                entry['weapon'] = result['name']
            except:
                IkaUtils.dprint('Exception occured in weapon recoginization.')
                IkaUtils.dprint(traceback.format_exc())

        return entry

    def isWin(self, context):
        return context['game']['won']

    def analyze(self, context):
        # 各プレイヤー情報のスタート左位置
        entry_left = 610
        # 各プレイヤー情報の横幅
        entry_width = 610
        # 各プレイヤー情報の高さ
        entry_height = 45
        entry_top = [101, 166, 231, 296, 431, 496, 561, 626]

        entry_id = 0

        context['game']['players'] = []

        img = context['engine']['frame']

        for top in entry_top:
            entry_id = entry_id + 1
            img_entry = img[top:top + entry_height,
                            entry_left:entry_left + entry_width]

            e = self.analyzeEntry(img_entry)

            e['team'] = 1 if entry_id < 4 else 2
            e['rank_in_team'] = entry_id if entry_id < 4 else entry_id - 4

            context['game']['players'].append(e)

            if e['me']:
                context['game']['won'] = True if entry_id < 5 else False

        context['game']['won'] = self.isWin(context)
        context['game']['timestamp'] = datetime.now()

    def match(self, context):
        return IkaUtils.matchWithMask(context['engine']['frame'], self.winlose_gray, 0.997, 0.20)

    def __init__(self):
        winlose = cv2.imread('masks/result_detail.png')

        try:
            self.weapons = IkaGlyphRecoginizer()
            self.weapons.loadModelFromFile("data/weapons.trained")
        except:
            IkaUtils.dprint("Could not initalize weapons recoginiton model")

        try:
            self.kd_recoginizer = IkaKdRecoginizer()
            self.kd_recoginizer.loadModelFromFile('data/kd.model')
            self.kd_recoginizer.train()
        except:
            IkaUtils.dprint("Could not initalize KD recoginiton model")
            self.kd_recoiginizer = None

        try:
            self.udemae_recoginizer = IkaUdemaeRecoginizer()
        except:
            IkaUtils.dprint("Could not initalize Udemae recoginiton model")
            self.udemae_recoginizer = None

        if winlose is None:
            print("勝敗画面のマスクデータが読み込めませんでした。")

        self.winlose_gray = cv2.cvtColor(winlose, cv2.COLOR_BGR2GRAY)

if __name__ == "__main__":
    import re
    files = sys.argv[1:]

    for file in files:
        target = cv2.imread(file)
        cv2.imshow('input', target)
        obj = IkaScene_ResultDetail()

        context = {
            'engine': {'frame': target},
            'game': {},
        }

        matched = obj.match(context)
        analyzed = obj.analyze(context)
        won = IkaUtils.getWinLoseText(
            context['game']['won'], win_text="win", lose_text="lose", unknown_text="unknown")
        print("matched %s analyzed %s result %s" % (matched, analyzed, won))

        print('')
        for e in context['game']['players']:

            if 'prefix' in e:
                prefix = e['prefix']
                prefix_ = re.sub('の', '', prefix)
                gender = e['gender']
            else:
                prefix_ = ''
                gender = ''

            kills = e['kills'] if not e['kills'] is None else ''
            deaths = e['deaths'] if not e['deaths'] is None else ''

            print("%s/%s %s%s" % (kills, deaths, prefix_, gender))
        # cv2.waitKey()

    # ランクごとにソートした画像を出す
    plot_img = np.zeros((2000, 1000, 1), np.uint8)
    x = 0
    y = 0
    for rank in obj.rank_imgs.keys():
        print(rank)
        for img in obj.rank_imgs[rank]:
            w = img.shape[1]
            h = img.shape[0]
            x1 = x
            x2 = x + w
            y1 = y
            y2 = y + h
            plot_img[y1:y2, x1:x2, 0] = img
            y = y2

        x = x + 100
        y = 0
    cv2.imshow('rank betu', plot_img)

    cv2.waitKey()
