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
import time

import cv2
import numpy as np

from ikalog.constants import special_weapons_v2
from ikalog.ml.classifier import ImageClassifier
from ikalog.scenes.stateful_scene import StatefulScene
from ikalog.utils import *
from ikalog.utils.character_recoginizer import *

from ikalog.utils.ikamatcher2.matcher import MultiClassIkaMatcher2 as MultiClassIkaMatcher

##
# Spl2GameSpecialWeaponActivation
#
# Detects if any special weapons are activated.
#
# EVENTS:
#
#     on_game_special_weapon(self, context, params)
#     Notifies special weapon activation in my team.
#
#     params['special_weapon']: id of special_weapon
#     params['me']: True is my special, otherwise False
#     params['msec']: timestamp (in milliseconds) or None
#
# HOW TO MANIPULATE THE MASKS:
#
#     This scene needs masks for each languages.
#     We highly recommend using video capture in Switch console
#     to record the video for manipulating mask data & testing.
#     Additional utilities are available upon requests.
#
#     Filename of the samples should be:
#       masks/<IKALOG_LANG>/v2_game_special_activation_<SPECIAL_WEAPON_ID>.png
#


def _elect(self, context, votes):
    # count
    items = {}
    for vote in votes:
        if vote[1] is None:
            continue
        key = vote[1]
        items[key] = items.get(key, 0) + 1

    # return the best key
    sorted_keys = sorted(
        items.keys(), key=lambda x: items[x], reverse=True)
    sorted_keys.extend([None])  # fallback

    return sorted_keys[0]


"""
ROI: Track the event in the region
"""
class ROI():
    def __init__(self, x, y, width, height, next_roi=None, prev_roi=None, raise_event=None):
        self.x = x
        self.y = y
        self.width = width
        self.height = height
        self.next = next_roi
        self.prev = prev_roi
        self.raise_event = raise_event
        self.disable()

    def disable(self):
        """
        Mark this ROI as disabled.
        """

        # Reset state
        self.triggered = False
        self.votes = []
        self.state = self.state_disabled

        if self.next:
            self.next.disable()

    def enable(self):
        """
        Mark this ROI as enabled.
        Detection will be performed.
        """
        self.triggered = False
        self.state = self.state_enabled

    def start_tracking(self):
        """
        Mark this ROI as tracking state.
        """
        self.state = self.state_tracking

        # The next ROI will be activated.
        self.next.enable()

    def cooldown(self):
        """
        Mark this ROI as cool-down state.
        Detection will be resumed later.
        """
        if self.triggered and self.start_time:
            self.state = self.state_cooldown
        else:
            self.enable()

    def extract_patch(self, frame):
        """
        Extract ROI image from the frame
        """
        return frame[self.y: self.y + self.height, self.x: self.x + self.width, :]

    def _is_my_special(self, img_special_bgr):
        # FIXME: Borrowed from IkaLog for Splatoon 1?, but not accurate
        img_special_bgr = img_special_bgr
        img = img_special_bgr[:, :150]

        img_s = cv2.cvtColor(img, cv2.COLOR_BGR2HSV)[:, :, 2]
        img_s[matcher.MM_WHITE()(img) > 127] = 127

        img_s_hist = cv2.calcHist(img_s[:, :], [0], None, [5], [0, 256])
        img_s_hist_black = float(np.amax(img_s_hist[0:1]))
        img_s_hist_non_black = float(np.amax(img_s_hist[3:4]))
        return img_s_hist_black < img_s_hist_non_black

    def state_disabled(self, scene, context):
        """
        Disabled - nothing to do.
        """

        #print("ROI (y=%d) is disabled" % self.y)
        pass

    def _detect_first(self, scene, context, img_special_bgr):
        # match phase 1: should have white
        img_special_white_gray = matcher.MM_WHITE()(img_special_bgr)
        img = img_special_white_gray

        # match phase 2: multi-class IkaMatcher
        probability, best_special_weapon = scene.masks.match_best(
            img_special_bgr)
        if not best_special_weapon:
            return None

        special_weapon_id = best_special_weapon.id

        # match phase 3: color distribution
        criteria = (cv2.TERM_CRITERIA_EPS +
                    cv2.TERM_CRITERIA_MAX_ITER, 10, 1.0)
        flags = cv2.KMEANS_RANDOM_CENTERS

        img_special_hsv_f32 = np.array(
            cv2.cvtColor(img_special_bgr, cv2.COLOR_BGR2GRAY))

        x = np.array(img_special_bgr, dtype=np.float32) / 255
        compactness, labels, centers = cv2.kmeans(
            x[:, :, 1], 4, None, criteria, 1, flags)
#        print("compactness", compactness)

        if compactness < 50:
            return None  # あってる?


#        print("best_weapon_id", special_weapon_id)
        return special_weapon_id

    def _detect_continue(self, scene, context, img_special_bgr):
        diff = 100000
        # match phase 1:
        if 0:
            img_special_bgr_i32 = np.array(img_special_bgr, dtype=np.int32)
            img_diff = np.abs(img_special_bgr_i32 -
                              self.img_special_last_bgr_i32)
            img_diff_bgr = np.array(img_diff, dtype=np.uint8)
            diff = np.sum(img_diff) / 255 / 3
            img = img_diff_bgr

            #print(img.shape, diff)
        if diff < 1000:
            self.img_special_last_bgr_i32 = img_special_bgr_i32

            cv2.imshow("patch @ %d" % self.y, img)
#            cv2.waitKey(1000)

            return self.special_weapon_id

        # if the match fails, try _detect_first
        return self._detect_first(scene, context, img_special_bgr)

    def state_enabled(self, scene, context):
        """
        Enable - perform the detection and switch to Tracking state.
        """

        # If the previous ROI is not active, move to Disabled state.
        prev = self.prev
        if prev and (prev.state in (prev.state_enabled, prev.state_disabled)):
            self.disable()

        # Extract
        frame = context['engine']['frame']
        img_special_bgr = self.extract_patch(frame)

        # Detect
        special_weapon_id = self._detect_first(scene, context, img_special_bgr)

        img = img_special_bgr

        if not special_weapon_id:
            return False

        # Switch to "tracking" state
        img_special_bgr_i32 = np.array(img_special_bgr, dtype=np.int32)
        self.img_special_last_bgr_i32 = img_special_bgr_i32

        self.state = self.state_tracking
        self.start_time = context['engine'].get('msec')
        self.special_weapon_id = special_weapon_id

        self.next.enable()

    def state_tracking(self, scene, context):
        """
        Tracking - perform the contiguous detection, until the object done.
        """
        force_elect = False  # Flag to perform election in this cycle

        #print("Special Weapon %s ROI (y=%d) is tracking" % (self.special_weapon_id, self.y))

        # Extract
        frame = context['engine']['frame']
        img_special_bgr = self.extract_patch(frame)

        special_weapon_id = self._detect_continue(
            scene, context, img_special_bgr)

        if not self.triggered:
            if special_weapon_id:
                # MEMO: Timing information is not used in this scene
                self.votes.append(
                    (context['engine'].get('msec'), special_weapon_id))

            if len(self.votes) > 10:
                force_elect = True

        # Timeout
        msec = context['engine'].get('msec')
        if msec:
            timeout = self.start_time + 4000  # should be 4000 (4s)
            if timeout < msec:
                self.cooldown()
                force_elect = len(self.votes) > 3

        if force_elect and self.raise_event and not self.triggered:
            self.raise_event('on_game_special_weapon', {
                'special_weapon': special_weapon_id,
                'me': self._is_my_special(img_special_bgr),
                'msec': self.start_time,
            })
            self.triggered = True

        matched = special_weapon_id is not None
        return matched

    def state_cooldown(self, scene, context):
        """
        Cool-down: Delay next detection (to prevent chattering)
        """
        #print("Special Weapon ROI (y=%d) is cooldown" % (self.y))

        msec = context['engine'].get('msec')
        if msec:
            timeout = self.start_time + 5000
            leave = timeout < msec
        else:
            leave = True

        if leave:
            self.enable()  # leave cooldown state


class Spl2GameSpecialWeaponActivation(StatefulScene):

    def reset(self):
        """Engine reset"""
        super(Spl2GameSpecialWeaponActivation, self).reset()
        self.img_last_special = None

        self.roi_list[0].disable()  # disable all ROIs
        self.roi_list[0].enable()

    def _raise_event_handler(self, event_name, params={}):
        """
        handler to receive events from ROI objects
        """
        self._call_plugins(event_name, params)

    def precheck(self, context):
        """
        check if the prequisties for special_weaapon detection are met.

        return
        True:  Perform detection.
        False: Skip detection
        """
        frame = context['engine']['frame']
        if frame is None:
            return False

        # pass matching in some scenes.
        session = self.find_scene_object('Spl2GameSession')
        if session is not None:
            if not (session._state.__name__ in ('_state_battle')):
                return False
        return True

    def _state_default(self, context):
        if not self.precheck(context):
            return False

        r = False
        for roi in self.roi_list:
            matched = roi.state(self, context)
            r = r or matched

            draw = True

            if self.preview:
                if roi.state == roi.state_disabled:
                    color = (0, 0, 0)
                elif roi.state == roi.state_enabled:
                    color = (90, 90, 90)
                elif roi.state == roi.state_cooldown:
                    color = (0, 0, 90)
                elif roi.state == roi.state_tracking:
                    color = (0, 255, 0) if matched else (0, 0, 255)
                    cv2.putText(context['engine']['preview'], text=roi.special_weapon_id or 'None', org=(
                        roi.x, roi.y - 5), fontFace=cv2.FONT_HERSHEY_SIMPLEX, fontScale=0.7, color=(0, 255, 0), thickness=2, lineType=cv2.LINE_4)

                cv2.rectangle(context['engine']['preview'],
                              pt1=(roi.x, roi.y),
                              pt2=(roi.x + roi.width, roi.y + roi.height),
                              color=color,
                              thickness=2,
                              lineType=cv2.LINE_4,
                              shift=0)

        return r

    def dump(self, context):
        # Not implemented :\
        pass

    def _analyze(self, context):
        pass

    # Called only once on initialization.
    def _init_scene(self, debug=False, preview=True):
        #
        # To gather mask data, enable this.
        #
        self.write_samples = False
        self.preview = preview

        # location of ROI
        self.width = 105
        self.height = 42
        self.left = 1073
        roi_top_list = [159 + 53 * 3, 159 + 53 *
                        2, 159 + 53 * 1, 159 + 53 * 0]  # FIXME

        self.masks = MultiClassIkaMatcher()
        for special_weapon in special_weapons_v2.keys():
            try:
                mask = IkaMatcher(
                    self.left, roi_top_list[-1], self.width, self.height,
                    img_file='v2_game_special_activation_%s.png' % special_weapon,
                    threshold=0.95,
                    orig_threshold=0.03,
                    bg_method=matcher.MM_NOT_WHITE(),
                    fg_method=matcher.MM_WHITE(),
                    label='special/%s' % special_weapon,
                    call_plugins=self._call_plugins,
                    debug=debug,
                )
                mask.id = special_weapon
                self.masks.add_mask(mask)
            except FileNotFoundError:
                IkaUtils.dprint('%s: Failed to load mask for %s' %
                                (self, special_weapon))
                pass

        self.roi_list = []
        next_roi = None
        for top in roi_top_list:
            roi = ROI(self.left, top, self.width, self.height,
                      next_roi, raise_event=self._raise_event_handler)
            if next_roi:
                next_roi.prev = roi
            self.roi_list.insert(0, roi)
            next_roi = roi

        # obosolete
        self._c = ImageClassifier(object)
        self._c.load_from_file(
            'data/spl2/spl2.game.special_weapon_activation.dat')

        self.reset()  # to initialize ROIs


if __name__ == "__main__":
    Spl2GameSpecialWeaponActivation.main_func()
