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

from ikalog.utils import *


class IkaScene_GameStart:

    # 720p サイズでの値
    mapname_width = 430
    mapname_left = 1280 - mapname_width
    mapname_top = 580
    mapname_height = 640 - mapname_top

    rulename_left = 640 - 120
    rulename_right = 640 + 120
    rulename_width = rulename_right - rulename_left
    rulename_top = 250
    rulename_bottom = 310
    rulename_height = rulename_bottom - rulename_top

    def guess_map(self, frame):
        # マップ名を判断
        for map in self.map_list:
            r = map['mask'].match(frame)
            if r:
                return map
        return None

    def guess_rule(self, frame):
        # モード名を判断
        for rule in self.rule_list:
            r = rule['mask'].match(frame)
            if r:
                return rule
        return None

    def elect(self, context):
        # 古すぎる投票は捨てる
        election_start = context['engine']['msec'] - self.election_period
        while (len(self.votes) and self.votes[0][0] < election_start):
            del self.votes[0]

        # 考えづらいがゼロ票なら開票しない
        if len(self.votes) == 0:
            return None, None

        # 3秒以上たっていたら開票開始
        #election_start2 = context['engine']['msec'] - (3 * 1000)
        #if election_start2 < self.votes[0][0]:
        #    return None, None

        # 開票作業
        maps = {}
        rules = {}

        count = 0
        map_top = (0, None)  # 最高票数の tuple   (17[票], <IkaMatcher>)
        rule_top = (0, None)

        for vote in self.votes:
            if vote[1] is not None:
                map = vote[1]['name']
                maps[map] = maps[map] + 1 if map in maps else 1
                if  map_top[0] < maps[map]:
                    map_top = (maps[map], vote[1])

            if vote[2] is not None:
                rule = vote[2]['name']
                rules[rule] = rules[rule] + 1 if rule in rules else 1
                if  rule_top[0] < rules[rule]:
                    rule_top = (rules[rule], vote[2])

        # 必要票数
        quorum = 1 # max(3, len(self.votes) / 2)
        #print(maps)
        #print(rules)
        #print('quorum = %s' % quorum)

        # 必要票数が達しなかった場合
        if map_top[0] < quorum:
            map_top = (0, None)

        if rule_top[0] < quorum:
            rule_top = (0, None)

        # 必要票数に達したものだけ更新
        if map_top[1] is not None:
            context['game']['map'] = map_top[1]
        if rule_top[1] is not None:
            context['game']['rule'] = rule_top[1]
        #print(map_top, rule_top)

        return map_top[1], rule_top[1]

    def match(self, context):
        map = self.guess_map(context['engine']['frame'])
        rule = self.guess_rule(context['engine']['frame'])

        if not map is None:
            context['game']['map'] = map
        if not rule is None:
            context['game']['rule'] = rule

        if len(self.votes) or map or rule:
            self.votes.append((context['engine']['msec'], map, rule))

        self.elect(context)

        return (map or rule)

    def __init__(self, debug=False):
        self.election_period = 5 * 1000 # msec
        self.votes = []

        self.map_list = [
            {'name': 'タチウオパーキング', 'file': 'masks/gachi_tachiuo.png'},
            {'name': 'モズク農園',         'file': 'masks/nawabari_mozuku.png'},
            {'name': 'ネギトロ炭鉱',       'file': 'masks/gachi_negitoro.png'},
            {'name': 'アロワナモール',     'file': 'masks/nawabari_arowana.png'},
            {'name': 'デカライン高架下',   'file': 'masks/yagura_decaline.png'},
            {'name': 'Bバスパーク',        'file': 'masks/gachi_buspark.png'},
            {'name': 'ハコフグ倉庫',       'file': 'masks/gachi_hakofugu.png'},
            {'name': 'シオノメ油田',       'file': 'masks/gachi_shionome.png'},
            {'name': 'モンガラキャンプ場', 'file': 'masks/hoko_mongara.png'},
            {'name': 'ホッケふ頭',         'file': 'masks/nawabari_hokke.png'},
            {'name': 'ヒラメが丘団地',     'file': 'masks/nawabari_hirame.png'},
            {'name': 'マサバ海峡大橋',     'file': 'masks/nawabari_masaba.png'},
        ]

        self.rule_list = [
            {'name': 'ガチエリア',     'file': 'masks/gachi_tachiuo.png'},
            {'name': 'ガチヤグラ',     'file': 'masks/yagura_decaline.png'},
            {'name': 'ガチホコバトル', 'file': 'masks/hoko_mongara.png'},
            {'name': 'ナワバリバトル', 'file': 'masks/nawabari_mozuku.png'},
        ]

        for map in self.map_list:
            map['mask'] = IkaMatcher(
                self.mapname_left, self.mapname_top, self.mapname_width, self.mapname_height,
                img_file=map['file'],
                threshold=0.95,
                orig_threshold=0.20,
                false_positive_method=IkaMatcher.FP_FRONT_IS_WHITE,
                pre_threshold_value=230,
                label='map:%s' % map['name'],
                debug=False,
            )

        for rule in self.rule_list:
            rule['mask'] = IkaMatcher(
                self.rulename_left, self.rulename_top, self.rulename_width, self.rulename_height,
                img_file=rule['file'],
                threshold=0.95,
                orig_threshold=0.20,
                false_positive_method=IkaMatcher.FP_FRONT_IS_WHITE,
                pre_threshold_value=230,
                label='rule:%s' % rule['name'],
                debug=False,
            )

if __name__ == "__main__":
    target = cv2.imread(sys.argv[1])

    context = {
        'engine': {'frame': target, 'msec': 0, },
        'game': {},
    }

    obj = IkaScene_GameStart(debug=True)

    r = obj.match(context)

    print(r, context['game'])

    cv2.imshow('Scene', target)
    cv2.waitKey()
