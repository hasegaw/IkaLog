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

from IkaUtils import *

import cv2
import time
import sys

# IkaOutput_WeaponTraining: IkaLog Output Plugin for gathering weapon data for training
#
# Save screenshots on certain events


class IkaOutput_WeaponTraining:
    ##
    # onGameIndividualResult Hook
    # @param self      The Object Pointer
    # @param context   IkaLog context
    #

    def onGameIndividualResult(self, context, basename=None):
        if basename is None:
            basename = time.strftime("ikabattle_%Y%m%d_%H%M", time.localtime())
        i = 0
        for e in context['game']['players']:
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
    import IkaScene_ResultDetail
    import os

    args = sys.argv.copy()
    del args[0]

    for in_file in args:
        target = cv2.imread(in_file)
        basename, ext = os.path.splitext(os.path.basename(in_file))
        obj = IkaScene_ResultDetail.IkaScene_ResultDetail()

        context = {
            'engine': {'frame': target},
            'game': {'map': {'name': ''}, 'rule': {'name': ''}},
        }

        matched = obj.match(context)
        analyzed = obj.analyze(context)
        won = IkaUtils.getWinLoseText(
            context['game']['won'], win_text="win", lose_text="lose", unknown_text="unknown")
        print("matched %s analyzed %s result %s" % (matched, analyzed, won))

        out = IkaOutput_WeaponTraining()
        out.onGameIndividualResult(context, basename=basename)
