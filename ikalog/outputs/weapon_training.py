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

from ikalog.utils import *


# IkaOutput_WeaponTraining: IkaLog Output Plugin for gathering weapon data for training
#
# Save screenshots on certain events


class WeaponTraining(object):
    ##
    # on_game_individual_result Hook
    # @param self      The Object Pointer
    # @param context   IkaLog context
    #

    def on_game_individual_result(self, context, basename=None):
        if basename is None:
            basename = time.strftime("ikabattle_%Y%m%d_%H%M", time.localtime())
        i = 0
        for e in context['game']['players']:
            if not ('weapon' in e):
                continue
            destdir = "%s/%s" % (self.dest_dir, e['weapon'])
            destfile = "%s/%s.%d.png" % (destdir, basename, i)
            print(destfile)
            try:
                os.makedirs(destdir)
            except:
                pass

            IkaUtils.writeScreenshot(destfile, e['img_weapon'])
            i = i + 1

    ##
    # Constructor
    # @param self         The Object Pointer.
    # @param dest_dir     Destionation directory (Relative path, or absolute path)
    #
    def __init__(self, dest_dir="training/weapons"):
        self.dest_dir = dest_dir


if __name__ == "__main__":
    from ikalog.scenes import result_detail
    import os

    for in_file in sys.argv[1:]:
        target = cv2.imread(in_file)

        if target is None:
            continue
        if (target.shape[0] != 720) or (target.shape[1] != 1280) or (target.shape[2] != 3):
            continue

        basename, ext = os.path.splitext(os.path.basename(in_file))
        obj = result_detail.ResultDetail()

        context = {
            'engine': {'frame': target},
            'game': {'map': {'name': ''}, 'rule': {'name': ''}},
        }

        matched = obj.match(context)
        analyzed = obj.analyze(context)
        won = IkaUtils.getWinLoseText(
            context['game']['won'], win_text="win", lose_text="lose", unknown_text="unknown")
        print("matched %s analyzed %s result %s" % (matched, analyzed, won))

        out = WeaponTraining()
        out.on_game_individual_result(context, basename=basename)
