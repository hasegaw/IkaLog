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

        context['game']['lobby'] = {
            'type': 'tag',
        }

        if (r_tag_matching):
            context['game']['lobby']['state'] = 'matching'
        else:
            context['game']['lobby']['state'] = 'matched'

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

        context['game']['lobby'] = {
            'type': None,
            'state': None,
        }

        if (r_fes_matched):
            context['game']['lobby']['type'] = 'festa'
        else:
            context['game']['lobby']['type'] = 'public'

        if (r_pub_matching):
            context['game']['lobby']['state'] = 'matching'

        if (r_pub_matched or r_fes_matched):
            context['game']['lobby']['state'] = 'matched'

        return True

    def match(self, context):
        if self.match_public_lobby(context):
            return True

        if self.match_tag_lobby(context):
            return True

        # FIXME: match_private_lobby

        return False

    def __init__(self, debug=False):
        self.mask_rule = IkaMatcher(
            72, 269, 90, 25,
            img_file='masks/ui_lobby_public.png',
            threshold=0.80,
            orig_threshold=0.30,
            bg_method=matcher.MM_NOT_BLACK(),
            fg_method=matcher.MM_WHITE(),
            label='Pub/Rule',
            debug=debug
        )

        self.mask_stage = IkaMatcher(
            #0, 345, 737, 94,
            72, 386, 110, 35,
            img_file='masks/ui_lobby_public.png',
            threshold=0.80,
            orig_threshold=0.30,
            bg_method=matcher.MM_NOT_BLACK(),
            fg_method=matcher.MM_WHITE(),
            label='Pub/Stage',
            debug=debug
        )

        self.mask_tag_rule = IkaMatcher(
            #0, 220, 737, 94,
            126, 249, 76, 26,
            img_file='masks/ui_lobby_tag_matching.png',
            threshold=0.80,
            orig_threshold=0.30,
            bg_method=matcher.MM_NOT_BLACK(),
            fg_method=matcher.MM_WHITE(),
            label='Tag/Rule',
            debug=debug
        )

        self.mask_tag_stage = IkaMatcher(
            156, 360, 94, 36,
            img_file='masks/ui_lobby_tag_matching.png',
            threshold=0.80,
            orig_threshold=0.30,
            bg_method=matcher.MM_NOT_BLACK(),
            fg_method=matcher.MM_WHITE(),
            label='Tag/Stage',
            debug=debug
        )

        # 背景：緑、赤、黒　文字：白
        self.mask_matching = IkaMatcher(
            826, 37, 280, 34,
            img_file='masks/ui_lobby_public.png',
            threshold=0.90,
            orig_threshold=0.10,
            bg_method=matcher.MM_NOT_WHITE(),
            fg_method=matcher.MM_WHITE(),
            label='Matching',
            debug=debug
        )

        # 背景：緑、赤、黒　文字：黄色
        self.mask_matched = IkaMatcher(
            826, 37, 280, 34,
            img_file='masks/ui_lobby_public_matched.png',
            threshold=0.90,
            orig_threshold=0.10,
            bg_method=matcher.MM_COLOR_BY_HUE(
                hue=(30 - 5, 30 + 5), visibility=(200, 255)),
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
            orig_threshold=0.10,
            bg_method=matcher.MM_COLOR_BY_HUE(
                hue=(30 - 5, 30 + 5), visibility=(200, 255)),
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
            orig_threshold=0.10,
            bg_method=matcher.MM_NOT_WHITE(),
            fg_method=matcher.MM_WHITE(),
            label='TagMatching',
            debug=debug
        )

        self.mask_fes_matched = IkaMatcher(
            851, 383, 225, 30,
            img_file='masks/ui_lobby_fes_matched.png',
            threshold=0.90,
            orig_threshold=0.10,
            fg_method=matcher.MM_COLOR_BY_HUE(
                hue=(30 - 5, 30 + 5), visibility=(200, 255)),
            label='FestaMatched',
            debug=debug
        )

if __name__ == "__main__":
    target = cv2.imread(sys.argv[1])
    obj = Lobby(debug=True)

    context = {
        'engine': {'frame': target},
        'game': {},
    }

    matched = obj.match(context)
    print("matched %s" % (matched))
    print(context['game'])
    #cv2.imshow('target', target)
    cv2.waitKey()
