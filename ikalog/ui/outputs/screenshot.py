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

from ikalog.outputs import Screenshot as Screenshot

#from ikalog.utils.localization import Localization
#_ = Localization.gettext_translation('screenshot', fallback=True).gettext

def _(s):
    return s

class IkaUIScreenshot(Screenshot):
    def apply_ui(self):
        self.result_detail_enabled = self.checkResultDetailEnable.GetValue()
        self.dir = self.editDir.GetValue()

    def refresh_ui(self):
        self._internal_update = True
        self.checkResultDetailEnable.SetValue(self.result_detail_enabled)

        if not self.dir is None:
            self.editDir.SetValue(self.dir)
        else:
            self.editDir.SetValue('')

    def on_config_reset(self, context=None):
        self.config_reset()
        self.refresh_ui()

    def config_reset(self):
        self.result_detail_enabled = False
        self.dir = os.path.join(os.getcwd(), 'screenshots')

    def on_config_load_from_context(self, context):
        self.config_reset()
        try:
            conf = context['config']['screenshot']
        except:
            conf = {}

        if 'ResultDetailEnable' in conf:
            self.result_detail_enabled = conf['ResultDetailEnable']

        if 'Dir' in conf:
            self.dir = conf['Dir']

        self.refresh_ui()
        return True

    def on_config_save_to_context(self, context):
        context['config']['screenshot'] = {
            'ResultDetailEnable': self.result_detail_enabled,
            'Dir': self.dir,
        }

    def on_config_apply(self, context):
        self.apply_ui()

    def on_initialize_plugin(self, context):
#
#        engine = context['engine']['engine']
#        engine.set_service('screenshot_save', self.write_screenshot)
        super(IkaUIScreenshot, self).on_initialize_plugin(context)

    ##
    # Constructor
    # @param self         The Object Pointer.
    # @param dir          Destionation directory (Relative path, or absolute path)
    #
    def __init__(self, dest_dir=None):
#        self.result_detail_enabled = (not dest_dir is None)
#        self.dir = dest_dir
        super(IkaUIScreenshot, self).__init__(dest_dir=dest_dir)
