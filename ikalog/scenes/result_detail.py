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
import sys
import traceback
from datetime import datetime

import cv2

import numpy as np
from ikalog.utils import *


class ResultDetail(object):

    def is_entry_me(self, entry_img):
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

    # FixMe: character_recoginizer を使って再実装
    def guess_fes_title(self, img_fes_title):
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

        if (x2 - x1) < 4:
            return None, None, None

        # 最小枠で crop
        img_fes_title_new = img_fes_title[:, x1:x2]

        # ボーイ/ガールは経験上横幅 56 ドット
        gender_x1 = x2 - 36
        gender_x2 = x2
        img_fes_gender = img_fes_title_mask[:, gender_x1:gender_x2]
        # ふつうの/まことの/スーパー/カリスマ/えいえん
        img_fes_level = img_fes_title_mask[:, 0:52]

        try:
            if self.fes_gender_recoginizer:
                gender = self.fes_gender_recoginizer.match(
                    cv2.cvtColor(img_fes_gender, cv2.COLOR_GRAY2BGR))
        except:
            IkaUtils.dprint(traceback.format_exc())
            gender = None

        try:
            if self.fes_level_recoginizer:
                level = self.fes_level_recoginizer.match(
                    cv2.cvtColor(img_fes_level, cv2.COLOR_GRAY2BGR))
        except:
            IkaUtils.dprint(traceback.format_exc())
            level = None

        team = None

        return gender, level, team

    def analyze_entry(self, img_entry):
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
        entry_xoffset_score_p = entry_xoffset_nawabari_score + entry_width_nawabari_score
        entry_width_score_p = 20

        entry_xoffset_kd = 1185 - entry_left
        entry_width_kd = 31
        entry_height_kd = 21

        me = self.is_entry_me(img_entry)
        if me:
            weapon_left = entry_xoffset_weapon_me
            name_left = entry_xoffset_name_me
            rank_left = 2
        else:
            weapon_left = entry_xoffset_weapon
            name_left = entry_xoffset_name
            rank_left = 43

        img_rank = img_entry[20:45, rank_left:rank_left + 43]
        img_weapon = img_entry[:, weapon_left:weapon_left + entry_width_weapon]
        img_name = img_entry[:, name_left:name_left + entry_width_name]
        img_score = img_entry[
            :, entry_xoffset_nawabari_score:entry_xoffset_nawabari_score + entry_width_nawabari_score]
        img_score_p = img_entry[
            :, entry_xoffset_score_p:entry_xoffset_score_p + entry_width_score_p]
        ret, img_score_p_thresh = cv2.threshold(cv2.cvtColor(
            img_score_p, cv2.COLOR_BGR2GRAY), 230, 255, cv2.THRESH_BINARY)

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
            fes_gender, fes_level, fes_team = self.guess_fes_title(
                img_fes_title)

        # フェス中ではなく、 p の表示があれば(avg = 55.0) ナワバリ。なければガチバトル
        isRankedBattle = (not is_fes) and (
            np.average(img_score_p_thresh[:, :]) < 16)
        isNawabariBattle = (not is_fes) and (not isRankedBattle)

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
            entry['img_fes_title'] = img_fes_title

            if fes_gender and ('ja' in fes_gender):
                entry['gender'] = fes_gender['ja']

            if fes_level and ('ja' in fes_level):
                entry['prefix'] = fes_level['ja']

        if self.udemae_recoginizer and isRankedBattle:
            try:
                entry['udemae_pre'] = self.udemae_recoginizer.match(
                    entry['img_score']).upper()
            except:
                IkaUtils.dprint('Exception occured in Udemae recoginization.')
                IkaUtils.dprint(traceback.format_exc())

        if self.number_recoginizer:
            try:
                entry['rank'] = self.number_recoginizer.match_digits(
                    entry['img_rank'])
                entry['kills'] = self.number_recoginizer.match_digits(
                    entry['img_kills'])
                entry['deaths'] = self.number_recoginizer.match_digits(
                    entry['img_deaths'])
                if isNawabariBattle:
                    entry['score'] = self.number_recoginizer.match_digits(
                        entry['img_score'])

            except:
                IkaUtils.dprint('Exception occured in K/D recoginization.')
                IkaUtils.dprint(traceback.format_exc())

        if self.weapons and self.weapons.trained:
            try:
                result, distance = self.weapons.match(entry['img_weapon'])
                entry['weapon'] = result
            except:
                IkaUtils.dprint('Exception occured in weapon recoginization.')
                IkaUtils.dprint(traceback.format_exc())

        return entry

    def is_win(self, context):
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

            e = self.analyze_entry(img_entry)

            e['team'] = 1 if entry_id < 5 else 2
            e['rank_in_team'] = entry_id if e['team'] == 1 else entry_id - 4

            context['game']['players'].append(e)

            if e['me']:
                context['game']['won'] = True if entry_id < 5 else False

        context['game']['won'] = self.is_win(context)
        context['game']['timestamp'] = datetime.now()
        context['game']['is_fes'] = ('prefix' in context['game']['players'][0])

        return True

    def match(self, context):
        return IkaUtils.matchWithMask(context['engine']['frame'], self.winlose_gray, 0.997, 0.20)

    def __init__(self):
        winlose = cv2.imread('masks/result_detail.png')

        try:
            self.weapons = IkaGlyphRecoginizer()
            self.weapons.load_model_from_file("data/weapons.knn.data")
            self.weapons.knn_train()
            IkaUtils.dprint('Loaded weapons recoginization model.')
        except:
            IkaUtils.dprint("Could not initalize weapons recoginiton model")

        try:
            self.number_recoginizer = character_recoginizer.NumberRecoginizer()
        except:
            self.number_recoginizer = None

        try:
            self.udemae_recoginizer = character_recoginizer.UdemaeRecoginizer()
        except:
            self.udemae_recoginizer = None

        try:
            self.fes_gender_recoginizer = character_recoginizer.FesGenderRecoginizer()
        except:
            self.fes_gender_recoginizer = None

        try:
            self.fes_level_recoginizer = character_recoginizer.FesLevelRecoginizer()
        except:
            self.fes_gender_recoginizer = None

        if winlose is None:
            print("勝敗画面のマスクデータが読み込めませんでした。")

        self.winlose_gray = cv2.cvtColor(winlose, cv2.COLOR_BGR2GRAY)

if __name__ == "__main__":
    import re
    files = sys.argv[1:]

    obj = ResultDetail()
    for file in files:
        target = cv2.imread(file)
        cv2.imshow('input', target)

        context = {
            'engine': {'frame': target},
            'game': {},
        }

        matched = obj.match(context)
        analyzed = obj.analyze(context)
        won = IkaUtils.getWinLoseText(
            context['game']['won'], win_text="win", lose_text="lose", unknown_text="unknown")
        fes = context['game']['is_fes']
        print("matched %s analyzed %s result %s fest %s" % (matched, analyzed, won, fes))

        print('')
        for e in context['game']['players']:
            if 'prefix' in e:
                prefix = e['prefix']
                prefix_ = re.sub('の', '', prefix)
                gender = e['gender']
            else:
                prefix_ = ''
                gender = ''

            udemae = e['udemae_pre'] if ('udemae_pre' in e) else None
            rank = e['rank'] if ('rank' in e) else None
            kills = e['kills'] if ('kills' in e) else None
            deaths = e['deaths'] if ('deaths' in e) else None
            weapon = e['weapon'] if ('weapon' in e) else None
            score = e['score'] if ('score' in e) else None
            me = '*' if e['me'] else ''

            print("rank %s udemae %s %s/%s weapon %s score %s %s%s %s, team %s rank_in_team %s" %
                  (rank, udemae, kills, deaths, weapon, score, prefix_, gender, me, e['team'], e['rank_in_team']))

    if len(files) > 0:
        cv2.waitKey()
