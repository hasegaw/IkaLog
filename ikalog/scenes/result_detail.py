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

import copy
import datetime
import os
import pickle
import sys
import traceback
from datetime import datetime

import cv2
import numpy as np

from ikalog.scenes.stateful_scene import StatefulScene
from ikalog.utils import *
from ikalog.inputs.filters import OffsetFilter


class ResultDetail(StatefulScene):
    #
    # AKAZE ベースのオフセット／サイズ調整
    #

    def result_detail_normalizer(self, img):
        # キーポイントとして不要な部分を削除
        img = copy.deepcopy(img)
        cv2.rectangle(img, (0, 000), (680, 720), (0, 0, 0), -1)

        # 特徴画像の生成
        white_filter = matcher.MM_WHITE()
        dark_filter = matcher.MM_DARK(visibility=(0, 16))
        img_w = white_filter.evaluate(img)
        img_dark = 255 - dark_filter.evaluate(img)

        img_features = img_dark + img_w
        img_features[:, 1000:1280] = \
            img_dark[:, 1000:1280] - img_w[:, 1000:1280]
        # cv2.imshow('features', img_features)
        # cv2.waitKey(10000)

        return img_features

    def get_keypoints(self, img):
        detector = cv2.AKAZE_create()
        keypoints, descriptors = detector.detectAndCompute(
            img,
            None,
        )
        return keypoints, descriptors

    def filter_matches(self, kp1, kp2, matches, ratio=0.75):
        mkp1, mkp2 = [], []
        for m in matches:
            if len(m) == 2 and m[0].distance < m[1].distance * ratio:
                m = m[0]
                mkp1.append(kp1[m.queryIdx])
                mkp2.append(kp2[m.trainIdx])
        p1 = np.float32([kp.pt for kp in mkp1])
        p2 = np.float32([kp.pt for kp in mkp2])
        kp_pairs = zip(mkp1, mkp2)
        return p1, p2, kp_pairs

    def tuples_to_keypoints(self, tuples):
        new_l = []
        for point in tuples:
            pt, size, angle, response, octave, class_id = point
            new_l.append(cv2.KeyPoint(
                pt[0], pt[1], size, angle, response, octave, class_id))
        return new_l

    def keypoints_to_tuples(self, points):
        new_l = []
        for point in points:
            new_l.append((point.pt, point.size, point.angle, point.response, point.octave,
                          point.class_id))
        return new_l

    def load_model_from_file(self, filename):
        f = open(filename, 'rb')
        l = pickle.load(f)
        f.close()
        self.ref_image_geometry = l[0]
        self.ref_keypoints = self.tuples_to_keypoints(l[1])
        self.ref_descriptors = l[2]

    def save_model_to_file(self, filename):
        f = open(filename, 'wb')
        pickle.dump([
            self.ref_image_geometry,
            self.keypoints_to_tuples(self.ref_keypoints),
            self.ref_descriptors,
        ], f)
        f.close()

    def rebuild_model(self, dest_filename, src_filename=None, img=None, normalizer_func=None):
        if img is None:
            img = cv2.imread(src_filename, 0)

        assert img is not None

        if normalizer_func is not None:
            img = normalizer_func(img)

        assert img is not None

        self.ref_keypoints, self.ref_descriptors = \
            self.get_keypoints(img)

        self.ref_image_geometry = img.shape[:2]

        self.save_model_to_file(dest_filename)
        IkaUtils.dprint('%s: Created model data %s' % (self, dest_filename))

    def load_akaze_model(self):
        model_filename = os.path.join(
            IkaUtils.baseDirectory(), 'data', 'result_detail_features.akaze.model')

        try:
            self.load_model_from_file(model_filename)
            if self.ref_keypoints == None:
                raise
        except:
            IkaUtils.dprint(
                '%s: Failed to load akaze model. trying to rebuild...' % self)
            self.rebuild_model(
                model_filename,
                img=cv2.imread('data/result_detail_features.png'),
                normalizer_func=self.result_detail_normalizer
            )
            self.load_model_from_file(model_filename)

    def auto_warp(self, context):
        # 画面のオフセットを自動検出して image を返す (AKAZE利用)

        frame = context['engine'].get('frame', None)
        if frame is None:
            return None
        keypoints, descs = self.get_keypoints(
            self.result_detail_normalizer(frame))

        matcher = cv2.BFMatcher(cv2.NORM_HAMMING)
        raw_matches = matcher.knnMatch(
            descs,
            trainDescriptors=self.ref_descriptors,
            k=2
        )
        p2, p1, kp_pairs = self.filter_matches(
            keypoints,
            self.ref_keypoints,
            raw_matches,
        )

        if len(p1) >= 4:
            H, status = cv2.findHomography(p1, p2, cv2.RANSAC, 5.0)
            print('%d / %d  inliers/matched' % (np.sum(status), len(status)))
        else:
            H, status = None, None
            print('%d matches found, not enough for homography estimation' % len(p1))
            raise

        w = 1280
        h = 720
        corners = np.float32([[0, 0], [w, 0], [w, h], [0, h]])
        pts2 = np.float32([[0, 0], [w, 0], [w, h], [0, h]])
        pts1 = np.float32(cv2.perspectiveTransform(
            corners.reshape(1, -1, 2), H).reshape(-1, 2) + (0, 0))
        M = cv2.getPerspectiveTransform(pts1, pts2)

        # out = cv2.drawKeypoints(img2, keypoints1, None)
        new_frame = cv2.warpPerspective(frame, M, (w, h))

        # 変形した画像がマスクと一致するか？
        matched = IkaUtils.matchWithMask(
            new_frame, self.winlose_gray, 0.997, 0.20)
        if matched:
            return new_frame

        IkaUtils.dprint('%s: auto_warp() function broke the image.' % self)
        return None

    def auto_offset(self, context):
        # 画面のオフセットを自動検出して image を返す

        filter = OffsetFilter(self)
        filter.enable()

        # filter が必要とするので...
        self.out_width = 1280
        self.out_height = 720

        best_match = (context['engine']['frame'], 0.0, 0, 0)
        offset_list = [0, -5, -4, -3, -2, -1, 1, 2, 3, 4, 5]

        for ox in offset_list:
            for oy in offset_list:
                filter.offset = (ox, oy)
                img = filter.execute(context['engine']['frame'])
                IkaUtils.matchWithMask(
                    context['engine']['frame'], self.winlose_gray, 0.997, 0.20)
                score = self.mask_win.match_score(img)

                if not score[0]:
                    continue

                if best_match[1] < score[1]:
                    best_match = (img, score[1], ox, oy)

        if best_match[2] != 0 or best_match[3] != 0:
            IkaUtils.dprint('%s: Offset detected. (%d, %d)' %
                            (self, best_match[2], best_match[3]))

        return best_match[0]

    def is_entry_me(self, img_entry):
        # ヒストグラムから、入力エントリが自分かを判断
        if len(img_entry.shape) > 2 and img_entry.shape[2] != 1:
            img_me = cv2.cvtColor(img_entry[:, 0:43], cv2.COLOR_BGR2GRAY)
        else:
            img_me = img_entry[:, 0:43]

        img_me = cv2.threshold(img_me, 230, 255, cv2.THRESH_BINARY)[1]

        me_score = np.sum(img_me)
        me_score_normalized = 0
        try:
            me_score_normalized = me_score / (43 * 45 * 255 / 10)
        except ZeroDivisionError as e:
            me_score_normalized = 0

        #print("score=%3.3f" % me_score_normalized)

        return (me_score_normalized > 1)

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

    def analyze_team_colors(self, context, img):
        # スクリーンショットからチームカラーを推測
        assert 'won' in context['game']
        assert img is not None

        if context['game']['won']:
            my_team_color_bgr = img[115:116, 1228:1229]
            counter_team_color_bgr = img[452:453, 1228:1229]
        else:
            counter_team_color_bgr = img[115:116, 1228:1229]
            my_team_color_bgr = img[452:453, 1228:1229]

        my_team_color = {
            'rgb': cv2.cvtColor(my_team_color_bgr, cv2.COLOR_BGR2RGB).tolist()[0][0],
            'hsv': cv2.cvtColor(my_team_color_bgr, cv2.COLOR_BGR2HSV).tolist()[0][0],
        }

        counter_team_color = {
            'rgb': cv2.cvtColor(counter_team_color_bgr, cv2.COLOR_BGR2RGB).tolist()[0][0],
            'hsv': cv2.cvtColor(counter_team_color_bgr, cv2.COLOR_BGR2HSV).tolist()[0][0],
        }

        return (my_team_color, counter_team_color)

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

            if fes_gender and ('en' in fes_gender):
                entry['gender_en'] = fes_gender['en']

            if fes_level and ('boy' in fes_level):
                entry['prefix_en'] = fes_level['boy']

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

    def analyze(self, context):
        # 各プレイヤー情報のスタート左位置
        entry_left = 610
        # 各プレイヤー情報の横幅
        entry_width = 610
        # 各プレイヤー情報の高さ
        entry_height = 45
        entry_top = [101, 166, 231, 296, 431, 496, 561, 626]

        # auto_warp() or auto_offset() で画面位置の調整
        img = self.auto_warp(context)
        if img is not None:
            matched = IkaUtils.matchWithMask(
                img,
                self.winlose_gray, 0, 997, 0.20
            )
            if not matched:
                img = None

        if img is None:
            IkaUtils.dprint('%s: Falling back to auto_offset()' % self)
            img = self.auto_offset(context, img)

        # インクリング一覧
        context['game']['players'] = []
        entry_id = 0

        for entry_id in range(len(entry_top)):  # 0..7
            top = entry_top[entry_id]

            img_entry = img[top:top + entry_height,
                            entry_left:entry_left + entry_width]

            e = self.analyze_entry(img_entry)

            if e.get('rank',None) is None:
                continue

            # team, rank_in_team
            e['team'] = 1 if entry_id < 4 else 2
            e['rank_in_team'] = entry_id + \
                1 if e['team'] == 1 else entry_id - 3

            # won
            if e['me']:
                context['game']['won'] = (entry_id < 4)

            context['game']['players'].append(e)

            if 0:
                e_ = e.copy()
                for f in list(e.keys()):
                    if f.startswith('img_'):
                        del e_[f]
                print(e_)

        # チームカラー
        team_colors = self.analyze_team_colors(context, img)
        context['game']['my_team_color'] = team_colors[0]
        context['game']['counter_team_color'] = team_colors[1]

        # フェス関係
        context['game']['is_fes'] = ('prefix' in context['game']['players'][0])

        # そのほか
        # context['game']['timestamp'] = datetime.now()

        return True

    def reset(self):
        super(ResultDetail, self).reset()

        self._last_event_msec = - 100 * 1000

        self._match_start_msec = - 100 * 1000
        self._last_frame = None
        self._diff_pixels = []

    def _state_default(self, context):
        if self.matched_in(context, 30 * 1000):
            return False

        if self.is_another_scene_matched(context, 'GameTimerIcon'):
            return False

        frame = context['engine']['frame']

        if frame is None:
            return False

        matched = IkaUtils.matchWithMask(
            context['engine']['frame'], self.winlose_gray, 0.997, 0.20)

        if matched:
            self._match_start_msec = context['engine']['msec']
            self._switch_state(self._state_tracking)
        return matched

    def _state_tracking(self, context):
        frame = context['engine']['frame']

        if frame is None:
            return False

        # マッチ1: 既知のマスクでざっくり
        matched = IkaUtils.matchWithMask(
            context['engine']['frame'], self.winlose_gray, 0.997, 0.20)

        # マッチ2: マッチ1を満たした場合は、白文字が安定するまで待つ
        # 条件1: 前回のイメージとの白文字の diff が 0 pixel になること
        # 条件2: 過去n回文の白文字の diff が <10 pixels になること
        #        (ノイズが多いキャプチャデバイス向けの救済策)
        diff_pixels = None
        img_current_h_i16 = None

        matched_diff0 = False
        matched_diff10 = False

        if matched:
            img_current_bgr = frame[626:626+45, 640:1280]
            img_current_hsv = cv2.cvtColor(img_current_bgr, cv2.COLOR_BGR2HSV)
            img_current_h_i16 = np.array(img_current_hsv[:, :, 1], np.int16)

        if matched and (self._last_frame is not None):
            img_diff = abs(img_current_h_i16 - self._last_frame)
            img_diff_u8 = np.array(img_diff, np.uint8)

            img_white = self._white_filter.evaluate(img_current_bgr)
            img_diff_u8[img_white < 128] = 0
            img_diff_u8[img_diff_u8 < 16] = 0
            img_diff_u8[img_diff_u8 > 1] = 255

            # cv2.imshow('DIFF', img_diff_u8)
            # cv2.imshow('white', img_white)

            diff_pixels = int(np.sum(img_diff_u8) / 255)

        if img_current_h_i16 is not None:
            self._last_frame = img_current_h_i16

        if diff_pixels is not None:
            matched_diff0 = (diff_pixels == 0)

            self._diff_pixels.append(diff_pixels)
            if len(self._diff_pixels) > 4:
                self._diff_pixels.pop(0)
                matched_diff10 = np.max(self._diff_pixels) < 10

            # print('img_diff_pixels', diff_pixels, self._diff_pixels, matched_diff0, matched_diff10)

        # escaped: 1000ms 以上の非マッチが続きシーンを抜けたことが確定
        # matched2: 白文字が安定している(条件1 or 条件2を満たしている)
        # triggered: すでに一定時間以内にイベントが取りがされた
        escaped = not self.matched_in(context, 1000)
        matched2 = matched_diff0 or matched_diff10
        triggered = self.matched_in(
            context, 30 * 1000, attr='_last_event_msec')

        if matched2 and (not triggered):
            self.analyze(context)
            # self.dump(context)
            self._call_plugins('on_result_detail')
            self._call_plugins('on_game_individual_result')
            self._last_event_msec = context['engine']['msec']
            triggered = True

        if matched:
            return True

        if escaped:
            if (not triggered) and (len(self._diff_pixels) > 0):
                IkaUtils.dprint(''.join((
                    '%s: 戦績画面を検出しましたが静止画を認識できませんでした。考えられる原因\n' % self,
                    '  ・HDMIキャプチャデバイスからのノイズ入力が多い\n',
                    '　・ブロックノイズが多いビデオファイルを処理している\n',
                    '　・正しいフォーマットで画像が入力されていない\n',
                    '　min(diff_pixels): %s' % min(self._diff_pixels),
                )))

            self._match_start_msec = - 100 * 1000
            self._last_frame = None
            self._diff_pixels = []
            self._switch_state(self._state_default)

        return False

    def dump(self, context):
        matched = True
        analyzed = True
        won = IkaUtils.getWinLoseText(
            context['game']['won'], win_text="win", lose_text="lose", unknown_text="unknown")
        fes = context['game']['is_fes']
        print("matched %s analyzed %s result %s fest %s" %
              (matched, analyzed, won, fes))
        print('--------')
        for e in context['game']['players']:
            udemae = e['udemae_pre'] if ('udemae_pre' in e) else None
            rank = e['rank'] if ('rank' in e) else None
            kills = e['kills'] if ('kills' in e) else None
            deaths = e['deaths'] if ('deaths' in e) else None
            weapon = e['weapon'] if ('weapon' in e) else None
            score = e['score'] if ('score' in e) else None
            me = '*' if e['me'] else ''

            if 'prefix' in e:
                prefix = e['prefix']
                prefix_ = re.sub('の', '', prefix)
                gender = e['gender']
            else:
                prefix_ = ''
                gender = ''

            print("team %s rank_in_team %s rank %s udemae %s %s/%s weapon %s score %s %s%s %s" % (
                e.get('team', None),
                e.get('rank_in_team', None),
                e.get('rank', None),
                e.get('udemae_pre', None),
                e.get('kills', None),
                e.get('deaths', None),
                e.get('weapon', None),
                e.get('score', None),
                prefix_, gender,
                me,))
        print('--------')

    def _analyze(self, context):
        frame = context['engine']['frame']
        return True

    def _init_scene(self, debug=False):
        self.mask_win = IkaMatcher(
            651, 47, 99, 33,
            img_file='masks/result_detail.png',
            threshold=0.950,
            orig_threshold=0.05,
            bg_method=matcher.MM_NOT_WHITE(),
            fg_method=matcher.MM_WHITE(),
            label='result_detail:WIN',
            debug=debug,
        )

        winlose = cv2.imread('masks/result_detail.png')
        self.winlose_gray = cv2.cvtColor(winlose, cv2.COLOR_BGR2GRAY)
        self._white_filter = matcher.MM_WHITE()

        self.udemae_recoginizer = UdemaeRecoginizer()
        self.number_recoginizer = NumberRecoginizer()
        self.fes_gender_recoginizer = character_recoginizer.FesGenderRecoginizer()
        self.fes_level_recoginizer = character_recoginizer.FesLevelRecoginizer()

        self.weapons = WeaponRecoginizer()
        self.weapons.load_model_from_file()
        self.weapons.knn_train()

        self.load_akaze_model()

if __name__ == "__main__":
    ResultDetail.main_func()
