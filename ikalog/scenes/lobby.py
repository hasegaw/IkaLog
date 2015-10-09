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

from ikalog.utils import *


class Lobby(object):

    def match_tag_lobby(self, context):
        frame = context['engine']['frame']

        # 「ルール」「ステージ」
        if not self.mask_tag_rule.match(frame):
            return False

        if not self.mask_tag_stage.match(frame):
            return False

        r_tag_matching = self.mask_tag_matching.match(frame)
        r_tag_matched = self.mask_tag_matched.match(frame)

        matched = (r_tag_matching or r_tag_matched)
        matched = matched and not (r_tag_matching and r_tag_matched)

        if not matched:
            return False

        context['lobby'] = {
            'type': 'tag',
        }

        if (r_tag_matching):
            context['lobby']['state'] = 'matching'
        else:
            context['lobby']['state'] = 'matched'

        if r_tag_matched:
            # タッグ参加人数は?
            top_list = [76, 149, 215, 290]

            filter_yellow = matcher.MM_COLOR_BY_HUE(
                hue=(32 - 5, 32 + 5), visibility=(230, 255))

            for n in range(len(top_list)):
                top = top_list[n]
                img_ready = frame[top:top + 41, 1118:1118 + 51]
                img_ready_yellow = filter_yellow.evaluate(img_ready)

                # vチェックが付いていれば平均600ぐらい、
                # vチェックが付いていなければ真っ黒(0)ぐらいのはず
                # -> 500 で割った値が 1.0 超えているかで見る
                ready_score = np.sum(img_ready_yellow / 255) / 500
                print(n, ready_score)
                if ready_score < 1.0:
                    break

            # この時点で n は 0 を起点として Ready になっていない
            # (score < 1.0な) インクリングを指している。
            # なので matched の場合 n はタッグ人数と等価。
            context['lobby']['team_members'] = n

        return True

    def match_private_lobby(self, context):
        frame = context['engine']['frame']

        r = self.mask_private_rule.match(frame) and \
            self.mask_private_stage.match(frame)

        # r == False ならプライベートロビーではない
        if not r:
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

    def match_public_lobby(self, context):
        frame = context['engine']['frame']

        # 「ルール」「ステージ」
        if not self.mask_rule.match(frame):
            return False

        if not self.mask_stage.match(frame):
            return False

        # マッチング中は下記文字列のうちひとつがあるはず
        r_pub_matching = self.mask_matching.match(frame)
        r_pub_matched = self.mask_matched.match(frame)
        r_fes_matched = self.mask_fes_matched.match(frame)

        match_count = 0
        for matched in [r_pub_matching, r_pub_matched, r_fes_matched]:
            if matched:
                match_count = match_count + 1

        if match_count > 1:
            return False

        if (r_fes_matched):
            context['lobby']['type'] = 'festa'
            context['lobby']['type'] = 'matched'
            return True

        else:
            context['lobby']['type'] = 'public'

        if (r_pub_matching):
            context['lobby']['state'] = 'matching'

        elif (r_pub_matched):
            context['lobby']['state'] = 'matched'

        else:
            # FIXME: マスクを使って評価したほうがいい
            context['lobby']['type'] = 'festa'
            context['lobby']['state'] = 'matching'

        return True

    def match_any_lobby(self, context):
        if self.match_public_lobby(context):
            return True

        if self.match_tag_lobby(context):
            return True

        if self.match_private_lobby(context):
            return True

        return False

    def match(self, context):
        r = self.match_any_lobby(context)

        if not r:
            return False

        msec = context['engine']['msec']
        call_plugins = context['engine']['service']['callPlugins']

        if context['lobby'].get('state', None) == 'matching':
            last_matching = context['lobby'].get('last_matching', -60 * 1000)
            context['lobby']['last_matching'] = msec
            if (msec - last_matching) > (60 * 1000):
                # マッチングを開始した
                call_plugins('on_lobby_matching')

        if context['lobby'].get('state', None) == 'matched':
            last_matched = context['lobby'].get('last_matched', -60 * 1000)
            context['lobby']['last_matched'] = msec
            if (msec - last_matched) > (60 * 1000):
                # マッチングを開始した
                call_plugins('on_lobby_matched')

        return True

    def __init__(self, debug=False):
        self.mask_rule = IkaMatcher(
            72, 269, 90, 25,
            img_file='masks/ui_lobby_public.png',
            threshold=0.90,
            orig_threshold=0.15,
            bg_method=matcher.MM_BLACK(),
            fg_method=matcher.MM_WHITE(),
            label='Pub/Rule',
            debug=debug
        )

        self.mask_stage = IkaMatcher(
            72, 386, 110, 35,
            img_file='masks/ui_lobby_public.png',
            threshold=0.90,
            orig_threshold=0.15,
            bg_method=matcher.MM_BLACK(),
            fg_method=matcher.MM_WHITE(),
            label='Pub/Stage',
            debug=debug
        )

        self.mask_tag_rule = IkaMatcher(
            126, 249, 76, 26,
            img_file='masks/ui_lobby_tag_matching.png',
            threshold=0.90,
            orig_threshold=0.15,
            bg_method=matcher.MM_BLACK(),
            fg_method=matcher.MM_WHITE(),
            label='Tag/Rule',
            debug=debug
        )

        self.mask_tag_stage = IkaMatcher(
            156, 360, 94, 36,
            img_file='masks/ui_lobby_tag_matching.png',
            threshold=0.90,
            orig_threshold=0.15,
            bg_method=matcher.MM_BLACK(),
            fg_method=matcher.MM_WHITE(),
            label='Tag/Stage',
            debug=debug
        )

        # 背景：緑、赤、黒　文字：白
        self.mask_matching = IkaMatcher(
            826, 37, 280, 34,
            img_file='masks/ui_lobby_public.png',
            threshold=0.90,
            orig_threshold=0.15,
            bg_method=matcher.MM_BLACK(),
            fg_method=matcher.MM_WHITE(),
            label='Matching',
            debug=debug
        )

        # 背景：緑、赤、黒　文字：黄色
        self.mask_matched = IkaMatcher(
            826, 37, 280, 34,
            img_file='masks/ui_lobby_public_matched.png',
            threshold=0.90,
            orig_threshold=0.15,
            bg_method=matcher.MM_BLACK(),
            fg_method=matcher.MM_COLOR_BY_HUE(
                hue=(30 - 5, 30 + 5), visibility=(200, 255)),
            label='Matched',
            debug=debug
        )

        # 背景：暗い赤、黒　文字：黄色
        self.mask_tag_matched = IkaMatcher(
            826, 24, 280, 34,
            img_file='masks/ui_lobby_tag_matched.png',
            threshold=0.90,
            orig_threshold=0.50,
            bg_method=matcher.MM_COLOR_BY_HUE(
                hue=(150, 180), visibility=(0, 255)),
            fg_method=matcher.MM_COLOR_BY_HUE(
                hue=(30 - 5, 30 + 5), visibility=(200, 255)),
            label='TagMatched',
            debug=debug
        )

        # 背景：暗い赤、黒　文字：白
        self.mask_tag_matching = IkaMatcher(
            826, 24, 280, 34,
            img_file='masks/ui_lobby_tag_matching.png',
            threshold=0.90,
            orig_threshold=0.50,
            bg_method=matcher.MM_COLOR_BY_HUE(
                hue=(150, 180), visibility=(0, 255)),
            fg_method=matcher.MM_WHITE(),
            label='TagMatching',
            debug=debug
        )

        self.mask_fes_matched = IkaMatcher(
            851, 383, 225, 30,
            img_file='masks/ui_lobby_fes_matched.png',
            threshold=0.90,
            orig_threshold=0.15,
            bg_method=matcher.MM_BLACK(),
            fg_method=matcher.MM_COLOR_BY_HUE(
                hue=(30 - 5, 30 + 5), visibility=(200, 255)),
            label='FestaMatched',
            debug=debug
        )

        self.mask_private_rule = IkaMatcher(
            78, 133, 74, 24,
            img_file='masks/ui_lobby_private_matched.png',
            threshold=0.90,
            orig_threshold=0.15,
            bg_method=matcher.MM_BLACK(),
            fg_method=matcher.MM_WHITE(),
            label='lobby/private/matched/rule',
            debug=debug
        )

        self.mask_private_stage = IkaMatcher(
            78, 272, 93, 24,
            img_file='masks/ui_lobby_private_matched.png',
            threshold=0.80,
            orig_threshold=0.15,
            bg_method=matcher.MM_BLACK(),
            fg_method=matcher.MM_WHITE(),
            label='lobby/private/matched/stage',
            debug=debug
        )

        self.mask_private_matching_alpha = IkaMatcher(
            738, 39, 170, 27,
            img_file='masks/ui_lobby_private_matching.png',
            threshold=0.80,
            orig_threshold=0.15,
            bg_method=matcher.MM_NOT_WHITE(),
            fg_method=matcher.MM_WHITE(),
            label='lobby/private/matching/alpha',
            debug=debug
        )

        self.mask_private_matching_bravo = IkaMatcher(
            738, 384, 160, 26,
            img_file='masks/ui_lobby_private_matching.png',
            threshold=0.80,
            orig_threshold=0.15,
            bg_method=matcher.MM_NOT_WHITE(),
            fg_method=matcher.MM_WHITE(),
            label='lobby/private/matching/alpha',
            debug=debug
        )

        self.mask_private_stage = IkaMatcher(
            78, 272, 93, 24,
            img_file='masks/ui_lobby_private_matched.png',
            threshold=0.80,
            orig_threshold=0.15,
            bg_method=matcher.MM_BLACK(),
            fg_method=matcher.MM_WHITE(),
            label='lobby/private/matched/stage',
            debug=debug
        )

        self.mask_private_matched_alpha = IkaMatcher(
            737, 36, 240, 30,
            img_file='masks/ui_lobby_private_matched.png',
            threshold=0.80,
            orig_threshold=0.15,
            fg_method=matcher.MM_COLOR_BY_HUE(
                hue=(30 - 5, 30 + 5), visibility=(200, 255)),
            label='lobby/private/matched/a',
            debug=debug
        )

        self.mask_private_matched_bravo = IkaMatcher(
            737, 380, 240, 30,
            img_file='masks/ui_lobby_private_matched.png',
            threshold=0.80,
            orig_threshold=0.15,
            fg_method=matcher.MM_COLOR_BY_HUE(
                hue=(30 - 5, 30 + 5), visibility=(200, 255)),
            label='lobby/private/match/b',
            debug=debug
        )


def noop(context):
    pass

if __name__ == "__main__":
    target = cv2.imread(sys.argv[1])
    obj = Lobby(debug=True)

    context = {
        'engine': {'frame': target, 'msec': 0, 'service': {'callPlugins': noop}, },
        'game': {},
        'lobby': {},
    }

    matched = obj.match(context)
    print("matched %s" % (matched))
    print(context['lobby'])
    #cv2.imshow('target', target)
    cv2.waitKey()
