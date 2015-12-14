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


class GearpowerTraining(object):
    ##
    # on_game_individual_result Hook
    # @param self      The Object Pointer
    # @param context   IkaLog context
    #

    def on_result_gears(self, context, basename=None):
        if basename is None:
            basename = time.strftime("gearpower_%Y%m%d_%H%M", time.localtime())
        
        for n in range(len(context['scenes']['result_gears']['gears'])):
            gear = context['scenes']['result_gears']['gears'][n]
            for field in gear:
                if field == 'img_name':
                    continue
                elif field.startswith('img_') and field.replace('img_','') in gear:
                    print('  gear %d : %s' % (n, field))
                    destdir = "%s/%s" % (self.dest_dir, gear[field.replace('img_','')])
                    destfile = "%s/%s.%d%s.png" % (destdir, basename, n, field)
                    print('  gear %d : %s' % (n, field))
                    try:
                        os.makedirs(destdir)
                    except:
                        pass
                    IkaUtils.writeScreenshot(destfile, gear[field])


    ##
    # Constructor
    # @param self         The Object Pointer.
    # @param dest_dir     Destionation directory (Relative path, or absolute path)
    #
    def __init__(self, dest_dir="training/gearpower"):
        self.dest_dir = dest_dir


if __name__ == "__main__":
    from ikalog.scenes import result_gears
    import os

    obj = result_gears.ResultGears(None)
    out = GearpowerTraining()
    for in_file in sys.argv[1:]:
        target = cv2.imread(in_file)

        if target is None:
            continue
        if (target.shape[0] != 720) or (target.shape[1] != 1280) or (target.shape[2] != 3):
            continue

        basename, ext = os.path.splitext(os.path.basename(in_file))

        context = {
            'engine': {'frame': target, 'msec': 0, },
            'game': {'map': {'name': ''}, 'rule': {'name': ''}},'scenes':{},
        }

        matched = obj.match(context)
        analyzed = obj._analyze(context)
        

        out.on_result_gears(context, basename=basename)
