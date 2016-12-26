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

import os
import time

from ikalog.utils import *

class Screenshot(object):

    def generate_timestr(self, context):
        return time.strftime('%Y%m%d_%H%M%S',
                                time.localtime(IkaUtils.getTime(context)))

    def write_screenshot(self, frame, filename):
        if IkaUtils.writeScreenshot(filename, frame):
            IkaUtils.dprint('%s: Saved a screenshot %s' % (self, filename))
            return True

        IkaUtils.dprint('%s: Failed to save a screenshot %s' % (self, filename))
        return False

    ##
    # on_result_detail_still Hook
    # @param self      The Object Pointer
    # @param context   IkaLog context
    #
    def on_result_detail_still(self, context):
        if not self.result_detail_enabled:
            return

        timestr = self.generate_timestr(context)
        destfile = os.path.join(self.dir, 'ikabattle_%s.png' % timestr)

        self.write_screenshot(context['engine']['frame'], filename=destfile)


    def on_initialize_plugin(self, context):
        engine = context['engine']['engine']
        engine.set_service('screenshot_save', self.write_screenshot)

    ##
    # Constructor
    # @param self         The Object Pointer.
    # @param dir          Destionation directory (Relative path, or absolute path)
    #
    def __init__(self, dest_dir=None):
        self.result_detail_enabled = (not dest_dir is None)
        self.dir = dest_dir
