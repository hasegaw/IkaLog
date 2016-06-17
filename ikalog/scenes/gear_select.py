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
from ikalog.utils.icon_recoginizer import GearRecoginizer, GearPowerRecoginizer
import traceback
import pprint

import cv2
import numpy as np

from ikalog.scenes.stateful_scene import StatefulScene
from ikalog.utils import IkaMatcher, matcher


def features_gear(gear):
    img_gear_hsv = cv2.cvtColor(gear['img_gear'], cv2.COLOR_BGR2HSV)
    h, w, channels = img_gear_hsv.shape
    features = np.reshape(img_gear_hsv, h * w * channels)
    return features


class GearSelect(StatefulScene):

    def _extract_weapon_image(self, img_entry):
        return {
            'img_gear': img_entry[16:16 + 64, 21:21 + 75],
            'img_main': img_entry[94:94 + 24, 11:11 + 25],
            'img_sub1': img_entry[99:99 + 20, 39:39 + 21],
            'img_sub2': img_entry[99:99 + 20, 59:59 + 21],
            'img_sub3': img_entry[99:99 + 20, 83:83 + 21],
        }

    def _extract_weapons_from_page(self, context):
        """
        ギア選択画面からギア情報を抜き出す
        """

        img = context['engine']['frame']

        filter_purple = matcher.MM_COLOR_BY_HUE(
            hue=(146 - 10, 146 + 10), visibility=(30, 255))

        img_purple = filter_purple(img)
        img2_hsv = cv2.cvtColor(img, cv2.COLOR_BGR2HSV)
        img2_hsv[:, :, 2] = np.minimum(img2_hsv[:, :, 2], 255 - img_purple)
        img2 = cv2.cvtColor(img2_hsv, cv2.COLOR_HSV2BGR)

        pos_entries = [
            (83,  53), (83, 195), (83, 334),
            (225,  53), (225, 195), (225, 334),
            (369,  53), (369, 195), (369, 334),
            (503,  53), (503, 195), (503, 334),
        ]

        w = 140
        h = 143
        i = 0

        result_set = {'img_gears': []}
        array0to1280 = np.array(range(1280), dtype=np.int32)

        for pos in pos_entries:
            i = i + 1
            x = pos[0]
            y = pos[1]
            img_entry = img[y: y + h, x: x + w, :]

            img_entry_hsv = cv2.cvtColor(img_entry, cv2.COLOR_BGR2HSV)
            r, img_entry_threshold = cv2.threshold(
                img_entry_hsv[:, :, 2], 150, 255, cv2.THRESH_BINARY)

            # img_entry_threshold_gray = matcher.MM_NOT_BLACK()(img_entry_threshold)
            line_x = img_entry_threshold[20, :]
            line_y = img_entry_threshold[:, 60]

            line_x_border = np.extract(
                line_x > 128, array0to1280[0:len(line_x)])
            line_y_border = np.extract(
                line_y > 128, array0to1280[0:len(line_y)])

            # Exit the loop if there are 12 gears in the page.
            if line_x_border.shape[0] == 0 or line_y_border.shape[0] == 0:
                break

            x1 = np.amin(line_x_border)
            x2 = np.amax(line_x_border)
            y1 = np.amin(line_y_border)
            y2 = np.amax(line_y_border)

            self._call_plugins('on_mark_rect_in_preview', params=[
                (pos[0] + x1, pos[1] + y1), (pos[0] + x2, pos[1] + y2)
            ])

            img_entry_cropped = img_entry[y1: y2, x1: x2, :]
            img_entry_normalized = cv2.resize(img_entry_cropped, (112, 124))
            gear_data = self._extract_weapon_image(img_entry_normalized)

            result_set['img_gears'].append(gear_data)

        return result_set

    def _get_active_gear_type(self, context):
        img = context['engine']['frame']
        pos_list = [
            {'type': 'weapon',   'pos': (353, 543), },
            {'type': 'headgear', 'pos': (520, 543), },
            {'type': 'clothing', 'pos': (683, 543), },
            {'type': 'shoes',    'pos': (850, 543), },
        ]

        count_selected = 0
        for t in pos_list:
            y = t['pos'][1]
            x = t['pos'][0]
            w = 49
            h = 31
            gray_filter = matcher.MM_WHITE(visibility=(100, 200))
            img_selected = img[y:y + h, x:x + w, :]
            img_selected_gray = gray_filter(img_selected)

            selected = np.sum(img_selected_gray / 255) < 200
            if selected:
                count_selected = count_selected + 1
                selected_gear = t['type']

        #    print(t['type'], 'selected', selected,  np.sum(img_selected / 255), np.sum(img_selected_gray / 255))
        #    cv2.imshow(t['type'], img_selected_gray)

        if count_selected != 1:
            return None

        return selected_gear

    def _get_active_page_number(self, context):
        """
        ブキページが何ページ目か調べる
        """
        img = context['engine']['frame']

        img_pages = img[495:500, 250: 250 + 370]

        # At first, we want to know the pixel color of black/colored bullets.
        # Cluster the pixel values (in grayscale, or V-channel in HSV) using
        # K-Means.
        #
        #   ○ ○ ○ ● ○
        #
        # ○: black bullet (not selected)
        # ●: colorerd bullet
        # else: background

        img_pages_hsv = cv2.cvtColor(img_pages, cv2.COLOR_BGR2HSV)[:, :, 2]
        h, w = img_pages_hsv.shape[0:2]
        img_pages_v = np.array(
            np.amax(img_pages_hsv[:, :], axis=0), dtype=np.float32)

        criteria = (cv2.TERM_CRITERIA_EPS +
                    cv2.TERM_CRITERIA_MAX_ITER, 10, 1.0)
        ret, label, center = cv2.kmeans(
            img_pages_v, 4, None, criteria, 10, cv2.KMEANS_RANDOM_CENTERS)

        v_bullet_black, v_background, v_background2, v_bullet_active = np.sort(
            center.reshape(-1))

        # Then we want to know the class for each pixels. since `label` returned
        # from cv2.kmeans() doesn't gurrantee the order of classes, we want to
        # classify the pixels again.

        d = np.array((
            abs(img_pages_v - v_background),
            abs(img_pages_v - v_bullet_black),
            abs(img_pages_v - v_bullet_active),
        ))
        classes = np.argmin(d, axis=0)

        if 0:
            r = ''
            for c in classes:
                r = r + str(c)
            print(r)

        # Now the classes should be a array like:
        #
        # class[]:  000022200111001110011100111000000
        # pg:           1    2    3    4    5
        #
        #   class 0: background
        #   class 1: black bullet (page, not selected)
        #   class 2: active bullet
        #

        page = 0
        x = 0

        while x < len(classes):
            if classes[x] == 0:  # Skip the background pixels
                x = x + 1
                continue

            if classes[x] == 1:  # Black bullet
                page = page + 1
                while x < len(classes):
                    if classes[x] == 0:
                        break
                    x = x + 1

            elif classes[x] == 2:  # Active bullet
                page = page + 1
                return page

            x = x + 1

        return None

    def _detect_new_state(self, context):
        """
        Identify the state from current video frame.

        Phase 1: Check for two "Return" buttons in left-bottom
        Phase 2: Check for four items: weapons, headgears, clothes, shoes

        If passed all tests, return appropriate state.
        Otherwise, return default state.
        """

        frame = context['engine']['frame']
        r_type_sel = self._mask_button_exit.match(frame)
        r_gear_sel = self._mask_button_return.match(frame)
        if (r_type_sel and r_gear_sel) or (not (r_type_sel or r_gear_sel)):
            return self._state_default

        r_weapon = self._mask_weapon_unselected.match(frame)
        r_headgear = self._mask_head_unselected.match(frame)
        r_clothing = self._mask_clothing_unselected.match(frame)
        r_shoes = self._mask_shoes_unselected.match(frame)

        r = ((not r_weapon) and  r_headgear and r_clothing and r_shoes) or \
            ((not r_headgear) and r_weapon and r_clothing and r_shoes) or \
            ((not r_clothing) and r_weapon and r_headgear and r_shoes) or \
            ((not r_shoes) and r_weapon and r_headgear and r_clothing)

        if not r:
            return self._state_default

        if r_type_sel:
            return self._state_type_select

        elif r_gear_sel:
            return self._state_gear_select

        return self._state_default

    # scene state

    def reset(self):
        """
        Reset to initial state
        """

        super(GearSelect, self).reset()

        self._last_event_msec = - 100 * 1000
        self._state = self._state_default

    def _state_gear_select(self, context):
        """
        In gear select mode, and one of the types is active.
        """

        new_state = self._detect_new_state(context)
        if new_state != self._state_gear_select:
            self._switch_state(new_state)
            return new_state != self._state_default

        gear_type = self._get_active_gear_type(context)
        page = self._get_active_page_number(context)

        classifier = {
            'weapon': self._weapon_classifier,
            'headgear': self._headgear_classifier,
            'clothing': self._clothing_classifier,
            'shoes': self._shoes_classifier,
        }[gear_type]

        if classifier is None:
            # The scene is active, but nothing to do.
            return True

        r = self._extract_weapons_from_page(context)

        gear_ids = []
        for e in r['img_gears']:
            key = classifier.predict(e['img_gear'])
            abilities = []
            for part in ['main', 'sub1', 'sub2', 'sub3']:
                img = e['img_%s' % part]
                key_, distance = self.gear_ability_classifier.predict_slide(
                    img)
                e['ability_%s' % part] = key_
                abilities.append(key_)

            gear_ids.append([key[0], abilities])

        self._call_plugins('on_gear_select', params={
            'gear_type': gear_type,
            'page': page,
            'gears': gear_ids,
        })

    def _backproject(self):
        pos_entries = [
            (83,  53), (83, 195), (83, 334),
            (225,  53), (225, 195), (225, 334),
            (369,  53), (369, 195), (369, 334),
            (503,  53), (503, 195), (503, 334),
        ]

        n = 0
        for e in r['img_gears']:
            img = e['img_gear']
            (x, y) = pos_entries[n]
            x = x + 640
            (h, w) = img.shape[0:2]
            if 0:
                img2 = classifier.pca_backproject_test(
                    cv2.resize(img, (48, 48)))
                img2 = cv2.cvtColor(img2, cv2.COLOR_HSV2BGR)
                img2 = cv2.resize(img2, (w, h))
                context['engine']['preview'][y: y + h, x:x + w] = img2

#            print(key, distance)
                #cv2.imshow(key, img)
                # cv2.waitKey(1)

            n = n + 1

#        cv2.imshow('back project', cv2.resize(cv2.cvtColor(img2, cv2.COLOR_HSV2BGR), (128,128)))

    def _state_type_select(self, context):
        """
        In gear select mode, but all of types
        (weapon, headware, clothing, and shoess) are inactive.
        """

        new_state = self._detect_new_state(context)
        if new_state != self._state_type_select:
            self._switch_state(new_state)
            return new_state != self._state_default

        return True

    def _state_default(self, context):
        """
        Default state. look for gear select mode.
        """

        if self.is_another_scene_matched(context, 'GameTimerIcon'):
            return False

        new_state = self._detect_new_state(context)
        if new_state != self._state_default:
            self._switch_state(new_state)
            return True

        return False

    def _analyze(self, context):
        pass

    def _init_scene(self, debug=False):
        self._headgear_classifier = GearRecoginizer('data/gears_head.knn.data')
        self._headgear_classifier.load_model_from_file()
        self._headgear_classifier.knn_train()

        self._weapon_classifier = \
            GearRecoginizer('data/gears_weapon.knn.data')
        self._weapon_classifier.load_model_from_file()
        self._weapon_classifier.knn_train()

        self._clothing_classifier = \
            GearRecoginizer('data/gears_clothing.knn.data')
        self._clothing_classifier.load_model_from_file()
        self._clothing_classifier.knn_train()

        self._shoes_classifier = \
            GearRecoginizer('data/gears_shoes.knn.data')
        self._shoes_classifier.load_model_from_file()
        self._shoes_classifier.knn_train()

        self._mask_button_exit = IkaMatcher(
            56, 594, 84, 74,
            img_file='gear_select.png',
            threshold=0.90,
            orig_threshold=0.20,
            fg_method=matcher.MM_WHITE(visibility=(200, 255)),
            bg_method=matcher.MM_NOT_WHITE(),
            label='gear_select/exit',
            call_plugins=self._call_plugins,
            debug=debug
        )

        self._mask_button_return = IkaMatcher(
            76, 491, 105, 30,
            img_file='gear_select.png',
            threshold=0.90,
            orig_threshold=0.20,
            fg_method=matcher.MM_WHITE(visibility=(55, 255)),
            bg_method=matcher.MM_BLACK(),
            label='gear_select/return',
            call_plugins=self._call_plugins,
            debug=debug
        )

        self._mask_button_exit = IkaMatcher(
            56, 594, 84, 74,
            img_file='gear_select.png',
            threshold=0.90,
            orig_threshold=0.20,
            fg_method=matcher.MM_WHITE(visibility=(200, 255)),
            label='gear_select/exit',
            call_plugins=self._call_plugins,
            debug=debug
        )

        self._mask_weapon_unselected = IkaMatcher(
            353, 543, 49, 31,
            img_file='gear_select.png',
            threshold=0.90,
            orig_threshold=0.20,
            fg_method=matcher.MM_WHITE(visibility=(50, 255)),
            bg_method=matcher.MM_DARK(),
            label='gear_select/weapon_not_selected',
            call_plugins=self._call_plugins,
            debug=debug
        )

        self._mask_head_unselected = IkaMatcher(
            520, 543, 49, 31,
            img_file='gear_select.png',
            threshold=0.90,
            orig_threshold=0.20,
            fg_method=matcher.MM_WHITE(visibility=(50, 255)),
            bg_method=matcher.MM_DARK(),
            label='gear_select/weapon_not_selected',
            call_plugins=self._call_plugins,
            debug=debug
        )

        self._mask_clothing_unselected = IkaMatcher(
            683, 543, 49, 31,
            img_file='gear_select.png',
            threshold=0.90,
            orig_threshold=0.20,
            fg_method=matcher.MM_WHITE(visibility=(50, 255)),
            bg_method=matcher.MM_DARK(),
            label='gear_select/clothing_not_selected',
            call_plugins=self._call_plugins,
            debug=debug
        )

        self._mask_shoes_unselected = IkaMatcher(
            850, 543, 49, 31,
            img_file='gear_select.png',
            threshold=0.90,
            orig_threshold=0.20,
            fg_method=matcher.MM_WHITE(visibility=(50, 255)),
            bg_method=matcher.MM_DARK(),
            label='gear_select/shoes_not_selected',
            call_plugins=self._call_plugins,
            debug=debug
        )

        self.gear_ability_classifier = GearPowerRecoginizer()

if __name__ == "__main__":
    GearSelect.main_func()
