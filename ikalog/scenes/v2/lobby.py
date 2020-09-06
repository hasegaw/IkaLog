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

import cv2
import numpy as np

from ikalog.scenes.scene import Scene
from ikalog.utils import *

from ikalog.ml.classifier import ImageClassifier


class V2Lobby(Scene):

    def match_squad_lobby(self, context):
        frame = context['engine']['frame']

        # 「ルール」「ステージ」
        r_mandatory = self.mask_squad_rule.match(frame) and \
            self.mask_squad_stage.match(frame)

        if not r_mandatory:
            return False

        r_squad_matching = self.mask_squad_matching.match(frame)
        r_squad_matched = self.mask_squad_matched.match(frame)

        matched = (r_squad_matching or r_squad_matched)
        matched = matched and not (r_squad_matching and r_squad_matched)

        if not matched:
            return False

        context['lobby']['type'] = 'tag'

        if (r_squad_matching):
            context['lobby']['state'] = 'matching'
        else:
            context['lobby']['state'] = 'matched'

        if 1:  # if r_squad_matched:
            # タッグ参加人数は?
            top_list = [76, 149, 215, 290]

            filter_yellow = matcher.MM_COLOR_BY_HUE(
                hue=(32 - 5, 32 + 5), visibility=(230, 255))

            num_members = 0
            for n in range(len(top_list)):
                top = top_list[n]
                img_ready = frame[top:top + 41, 1118:1118 + 51]
                img_ready_yellow = filter_yellow(img_ready)

                # vチェックが付いていれば平均600ぐらい、
                # vチェックが付いていなければ真っ黒(0)ぐらいのはず
                # -> 500 で割った値が 1.0 超えているかで見る
                ready_score = np.sum(img_ready_yellow / 255) / 500
                if ready_score > 1.0:
                    num_members = num_members + 1

            context['lobby']['team_members'] = num_members

        return True

    def match_private_lobby(self, context):
        frame = context['engine']['frame']

        mandatory = self.mask_private_rule.match(frame) and \
            self.mask_private_stage.match(frame)

        if not mandatory:
            return False

        # Matching? or Matched?
        r_matching = self.mask_private_matching_alpha.match(frame) and \
            self.mask_private_matching_bravo.match(frame)

        r_matched = self.mask_private_matched_alpha.match(frame) and \
            self.mask_private_matched_bravo.match(frame)

        # マッチング中かつマッチング完了はありえない
        if (not (r_matching or r_matched)) or (r_matching and r_matched):
            return False

        context['lobby']['type'] = 'private'

        if r_matching:
            context['lobby']['state'] = 'matching'

        else:  # r_matched:
            context['lobby']['state'] = 'matched'

        return True

    def match_private_spectator_lobby(self, context):
        frame = context['engine']['frame']

        mandatory = (self.mask_private_matching_spectator.match(frame) or \
            self.mask_private_matched_spectator) and \
            self.mask_private_rule.match(frame) and \
            self.mask_private_stage.match(frame)

        if not mandatory:
            return False

        r_matching = self.mask_private_matching_spectator_alpha.match(frame) and \
            self.mask_private_matching_spectator_bravo.match(frame)

        r_matched = self.mask_private_matched_spectator_alpha.match(frame) and \
            self.mask_private_matched_spectator_bravo.match(frame)

        # マッチング中かつマッチング完了はありえない
        if (not (r_matching or r_matched)) or (r_matching and r_matched):
            return False

        context['lobby']['type'] = 'private'

        if r_matching:
            context['lobby']['state'] = 'matching'

        else:  # r_matched:
            context['lobby']['state'] = 'matched'

        # TODO: is spectating?

        filter_yellow = matcher.MM_COLOR_BY_HUE(
            hue=(32 - 5, 32 + 5), visibility=(230, 255))

        top_list = [572, 621]
        for n in range(len(top_list)):
            top = top_list[n]
            img_ready = frame[top:top + 38, 718:718 + 19]
            img_ready_yellow = filter_yellow(img_ready)

            spectator_score = np.sum(img_ready_yellow / 255) / 500
            print("SPEC SCORE", spectator_score)
            if spectator_score > 1.0:                   
                context['lobby']['spectator'] = True

        return True

    def match_public_lobby(self, context):
        frame = context['engine']['frame']

        # FIXME: Additional checks

        # 「ルール」「ステージ」
        # mandatory = self.mask_rule.match(frame) and \
        #    self.mask_stage.match(frame)

        # if not mandatory:
        #    return False

        # r = self.classifier_matching_status.new_predict_frame(
        #     context['engine']['frame'])

        r_pub_matching = self.mask_matching.match(frame)
        r_pub_matched = self.mask_matched.match(frame)
        r_fes_matched = False  # not yet

        # フェスの場合
        # FIXME: Festa, Matching の組み合わせ
        if (r_fes_matched):
            context['lobby']['type'] = 'festa'
            context['lobby']['state'] = 'matched'
            return True

        # パブリックロビー
        if r_pub_matching or r_pub_matched:
            context['lobby']['type'] = 'public'
            if r_pub_matching:
                context['lobby']['state'] = 'matching'

            elif r_pub_matched:
                context['lobby']['state'] = 'matched'

            return True
        return False

    def match_any_lobby(self, context):
        if (not 'lobby' in context):
            context['lobby'] = {}

        if self.match_public_lobby(context):
            return True

        if self.match_private_spectator_lobby(context):
            return True

        if self.match_private_lobby(context):
            return True

        return False

        if self.match_squad_lobby(context):
            return True


        return False

    def reset(self):
        super(V2Lobby, self).reset()

        self._last_matching_event_msec = - 100 * 1000
        self._last_matched_event_msec = - 100 * 1000

    def match_no_cache(self, context):
        if self.is_another_scene_matched(context, 'Spl2GameSession'):
            return False

        frame = context['engine']['frame']

        if frame is None:
            return False

        matched = self.match_any_lobby(context)

        if matched:
            if context['lobby'].get('state', None) == 'matching':
                if not self.matched_in(context, 60 * 1000, attr='_last_matching_event_msec'):
                    self._call_plugins('on_lobby_matching')
                self._last_matching_event_msec = context['engine']['msec']

            elif context['lobby'].get('state', None) == 'matched':
                if not self.matched_in(context, 60 * 1000, attr='_last_matched_event_msec'):
                    self._call_plugins('on_lobby_matched')
                self._last_matched_event_msec = context['engine']['msec']
            return True

        return False

    def _analyze(self, context):
        pass

    def dump(self, context):
        lobby = context['lobby']
        print('%s: matched %s type %s spectator %s state %s team_members %s' % (
            self,
            self._matched,
            lobby.get('type', None),
            lobby.get('spectator', None),
            lobby.get('state', None),
            lobby.get('team_members', None),
        ))

    def _init_scene(self, debug=False):
        # self.classifier_matching_status = ImageClassifier()
        # self.classifier_matching_status.load_from_file(
        #     'spl2.lobby.matching.dat')

        # self.mask_rule = IkaMatcher(
        #     72, 269, 90, 25,
        #     img_file='lobby_public_matched.png',
        #     threshold=0.90,
        #     orig_threshold=0.15,
        #     bg_method=matcher.MM_BLACK(),
        #     fg_method=matcher.MM_WHITE(),
        #     label='Pub/Rule',
        #     call_plugins=self._call_plugins,
        #     debug=debug
        # )

        # self.mask_stage = IkaMatcher(
        #     72, 386, 110, 35,
        #     img_file='lobby_public_matched.png',
        #     threshold=0.90,
        #     orig_threshold=0.15,
        #     bg_method=matcher.MM_BLACK(),
        #     fg_method=matcher.MM_WHITE(),
        #     label='Pub/Stage',
        #     call_plugins=self._call_plugins,
        #     debug=debug
        # )

        # self.mask_squad_rule = IkaMatcher(
        #     126, 249, 76, 26,
        #     img_file='lobby_squad_matching.png',
        #     threshold=0.90,
        #     orig_threshold=0.15,
        #     bg_method=matcher.MM_BLACK(),
        #     fg_method=matcher.MM_WHITE(),
        #     label='Tag/Rule',
        #     call_plugins=self._call_plugins,
        #     debug=debug
        # )

        # self.mask_squad_stage = IkaMatcher(
        #     156, 360, 94, 36,
        #     img_file='lobby_squad_matching.png',
        #     threshold=0.90,
        #     orig_threshold=0.15,
        #     bg_method=matcher.MM_BLACK(),
        #     fg_method=matcher.MM_WHITE(),
        #     label='Tag/Stage',
        #     call_plugins=self._call_plugins,
        #     debug=debug
        # )

        # self.mask_testfire = IkaMatcher(
        #     218, 84, 195, 32,
        #     img_file='v2_lobby_testfire.png',
        #     threshold=0.90,
        #     orig_threshold=0.30,
        #     bg_method=matcher.MM_NOT_WHITE(),
        #     fg_method=matcher.MM_WHITE(),
        #     label='v2_lobby_testfire',
        #     call_plugins=self._call_plugins,
        #     debug=debug
        # )

        # 背景：緑、赤、黒　文字：白
        self.mask_matching = IkaMatcher(
            804, 26, 277, 41,
            img_file='v2_lobby_matching.png',
            threshold=0.80,
            orig_threshold=0.30,
            bg_method=matcher.MM_BLACK(),
            fg_method=matcher.MM_WHITE(),
            label='Matching',
            call_plugins=self._call_plugins,
            debug=debug
        )

        # 背景：緑、赤、黒　文字：黄色
        self.mask_matched = IkaMatcher(
            804, 26, 277, 41,
            img_file='v2_lobby_matched.png',
            # threshold=0.80,
            # orig_threshold=0.30,
            # bg_method=matcher.MM_BLACK(),
            # fg_method=matcher.MM_COLOR_BY_HUE(
            #     hue=(55 - 5, 55 + 5), visibility=(200, 255)),
            threshold=0.90,
            orig_threshold=0.15,
            bg_method=matcher.MM_BLACK(),
            fg_method=matcher.MM_COLOR_BY_HUE(
                hue=(30 - 5, 30 + 5), visibility=(200, 255)),
            label='Matched',
            call_plugins=self._call_plugins,
            debug=debug
        )

        # # 背景：暗い赤、黒　文字：黄色
        # self.mask_squad_matched = IkaMatcher(
        #     826, 24, 280, 34,
        #     img_file='lobby_squad_matched.png',
        #     threshold=0.90,
        #     orig_threshold=0.50,
        #     bg_method=matcher.MM_COLOR_BY_HUE(
        #         hue=(150, 180), visibility=(0, 255)),
        #     fg_method=matcher.MM_COLOR_BY_HUE(
        #         hue=(30 - 5, 30 + 5), visibility=(200, 255)),
        #     label='TagMatched',
        #     call_plugins=self._call_plugins,
        #     debug=debug
        # )

        # # 背景：暗い赤、黒　文字：白
        # self.mask_squad_matching = IkaMatcher(
        #     826, 24, 280, 34,
        #     img_file='lobby_squad_matching.png',
        #     threshold=0.90,
        #     orig_threshold=0.50,
        #     bg_method=matcher.MM_COLOR_BY_HUE(
        #         hue=(150, 180), visibility=(0, 255)),
        #     fg_method=matcher.MM_WHITE(),
        #     label='TagMatching',
        #     call_plugins=self._call_plugins,
        #     debug=debug
        # )

        # self.mask_fes_matched = IkaMatcher(
        #     851, 383, 225, 30,
        #     img_file='lobby_festa_matched.png',
        #     threshold=0.90,
        #     orig_threshold=0.30,
        #     bg_method=matcher.MM_BLACK(),
        #     fg_method=matcher.MM_COLOR_BY_HUE(
        #         hue=(30 - 5, 30 + 5), visibility=(200, 255)),
        #     label='FestaMatched',
        #     call_plugins=self._call_plugins,
        #     debug=debug
        # )

        self.mask_private_rule = IkaMatcher(
            151, 185, 60, 22,
            img_file='v2_lobby_private_matched.png',
            threshold=0.80,
            orig_threshold=0.30,
            bg_method=matcher.MM_BLACK(),
            fg_method=matcher.MM_WHITE(),
            label='lobby/private/matched/rule',
            call_plugins=self._call_plugins,
            debug=debug
        )

        self.mask_private_stage = IkaMatcher(
            151, 279, 61, 30,
            img_file='v2_lobby_private_matched.png',
            threshold=0.80,
            orig_threshold=0.15,
            bg_method=matcher.MM_BLACK(),
            fg_method=matcher.MM_WHITE(),
            label='lobby/private/matched/stage',
            call_plugins=self._call_plugins,
            debug=debug
        )

        # Waiting for players - Private
        self.mask_private_matching_alpha = IkaMatcher(
            722, 95, 119, 30,
            img_file='v2_lobby_private_matching.png',
            threshold=0.80,
            orig_threshold=0.15,
            bg_method=matcher.MM_NOT_WHITE(),
            fg_method=matcher.MM_WHITE(),
            label='lobby/private/matching/a',
            call_plugins=self._call_plugins,
            debug=debug
        )

        self.mask_private_matching_bravo = IkaMatcher(
            722, 345, 120, 22,
            img_file='v2_lobby_private_matching.png',
            threshold=0.80,
            orig_threshold=0.15,
            bg_method=matcher.MM_NOT_WHITE(),
            fg_method=matcher.MM_WHITE(),
            label='lobby/private/matching/b',
            call_plugins=self._call_plugins,
            debug=debug
        )

        # BATTLE START - Private
        self.mask_private_matched_alpha = IkaMatcher(
            722, 95, 119, 30,
            img_file='v2_lobby_private_matched.png',
            threshold=0.80,
            orig_threshold=0.15,
            fg_method=matcher.MM_COLOR_BY_HUE(
                hue=(30 - 5, 30 + 5), visibility=(200, 255)),
            label='lobby/private/matched/a',
            call_plugins=self._call_plugins,
            debug=debug
        )

        self.mask_private_matched_bravo = IkaMatcher(
            722, 345, 120, 22,
            img_file='v2_lobby_private_matched.png',
            threshold=0.80,
            orig_threshold=0.15,
            fg_method=matcher.MM_COLOR_BY_HUE(
                hue=(30 - 5, 30 + 5), visibility=(200, 255)),
            label='lobby/private/match/b',
            call_plugins=self._call_plugins,
            debug=debug
        )

        # Waiting for confirm - With spectator
        self.mask_private_matching_spectator = IkaMatcher(
            722, 534, 117, 31,
            img_file='v2_lobby_private_matching_spectator.png',
            threshold=0.80,
            orig_threshold=0.15,
            bg_method=matcher.MM_NOT_WHITE(),
            fg_method=matcher.MM_WHITE(),
            label='lobby/private/matching_spectator/s',
            call_plugins=self._call_plugins,
            debug=debug
        )

        self.mask_private_matching_spectator_alpha = IkaMatcher(
            722, 32, 119, 30,
            img_file='v2_lobby_private_matching_spectator.png',
            threshold=0.80,
            orig_threshold=0.15,
            bg_method=matcher.MM_NOT_WHITE(),
            fg_method=matcher.MM_WHITE(),
            label='lobby/private/matching_spectator/a',
            call_plugins=self._call_plugins,
            debug=debug
        )

        self.mask_private_matching_spectator_bravo = IkaMatcher(
            722, 283, 120, 22,
            img_file='v2_lobby_private_matching_spectator.png',
            threshold=0.80,
            orig_threshold=0.15,
            bg_method=matcher.MM_NOT_WHITE(),
            fg_method=matcher.MM_WHITE(),
            label='lobby/private/matching_spectator/b',
            call_plugins=self._call_plugins,
            debug=debug
        )

        # BATTLE START - with spectator
        self.mask_private_matched_spectator = IkaMatcher(
            722, 534, 142, 25,
            img_file='v2_lobby_private_matched.png',
            threshold=0.80,
            orig_threshold=0.15,
            fg_method=matcher.MM_COLOR_BY_HUE(
                hue=(30 - 5, 30 + 5), visibility=(200, 255)),
            label='lobby/private/matched_spectator/s',
            call_plugins=self._call_plugins,
            debug=debug
        )

        self.mask_private_matched_spectator_alpha = IkaMatcher(
            722, 29, 142, 25,
            img_file='v2_lobby_private_matched.png',
            threshold=0.80,
            orig_threshold=0.15,
            fg_method=matcher.MM_COLOR_BY_HUE(
                hue=(30 - 5, 30 + 5), visibility=(200, 255)),
            label='lobby/private/matched_spectator/a',
            call_plugins=self._call_plugins,
            debug=debug
        )

        self.mask_private_matched_spectator_bravo = IkaMatcher(
            722, 283, 142, 25,
            img_file='v2_lobby_private_matched_spectator.png',
            threshold=0.80,
            orig_threshold=0.15,
            fg_method=matcher.MM_COLOR_BY_HUE(
                hue=(30 - 5, 30 + 5), visibility=(200, 255)),
            label='lobby/private/match/b',
            call_plugins=self._call_plugins,
            debug=debug
        )


if __name__ == "__main__":
    V2Lobby.main_func()
