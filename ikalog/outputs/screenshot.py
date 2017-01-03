#!/usr/bin/env python3
# -*- coding: utf-8 -*-
#
#  IkaLog
#  ======
#  Copyright (C) 2016 Takeshi HASEGAWA
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

from ikalog.plugin import IkaLogPlugin
from ikalog.utils import *


class ScreenshotPlugin(IkaLogPlugin):

    def generate_timestr(self, context=None):
        t = time.time() if context is None else IkaUtils.getTime(context)
        return time.strftime('%Y%m%d_%H%M%S', time.localtime(t))

    def write_screenshot(self, frame, filename=None):
        if filename is None:
            filename = 'snapshot%s.png' % self.generate_timestr()

        if filename == os.path.basename(filename):
            filename = os.path.join(self.config['dest_dir'], filename)

        if IkaUtils.writeScreenshot(filename, frame):
            IkaUtils.dprint('%s: Saved a screenshot %s' % (self, filename))
            return True

        IkaUtils.dprint('%s: Failed to save a screenshot %s' %
                        (self, filename))
        return False

    def on_validate_configuration(self, config):
        assert config['dest_dir'] is not None
        assert os.path.exists(config['dest_dir'])
        assert config['enabled'] in [True, False]
        return True

    def on_reset_configuration(self):
        self.config['dest_dir'] = 'screeenshots/'
        self.config['enabled'] = False

    def on_set_configuration(self, config):
        self.config['dest_dir'] = config['dest_dir']
        self.config['enabled'] = config['enabled']

    def on_result_detail_still(self, context):
        if not self.config['enabled']:
            return

        timestr = self.generate_timestr(context)
        destfile = os.path.join(
            self.config['dest_dir'], 'ikabattle_%s.png' % timestr)

        self.write_screenshot(context['engine']['frame'], filename=destfile)

    def on_initialize_plugin(self, context):
        engine = context['engine']['engine']
        engine.set_service('screenshot_save', self.write_screenshot)
        engine.set_service('screenshot_get_configuration',
                           self.get_configuration)
        engine.set_service('screenshot_set_configuration',
                           self.set_configuration)

    ##
    # Constructor
    # @param self         The Object Pointer.
    # @param dir          Destionation directory (Relative path, or absolute path)
    #
    def __init__(self, dest_dir=None):
        super(ScreenshotPlugin, self).__init__()


class Screenshot(ScreenshotPlugin):

    def __init__(self, dest_dir=None):
        super(Screenshot, self).__init__()

        config = self.get_configuration()
        config['dest_dir'] = dest_dir
        config['enabled'] = True
        self.set_configuration(config)
