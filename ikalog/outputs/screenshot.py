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

from ikalog.scenes.plaza_user_stat import *  # Fixme...


# Needed in GUI mode
try:
    import wx
except:
    pass

_ = Localization.gettext_translation('screenshot', fallback=True).gettext

# IkaOutput_Screenshot: IkaLog Output Plugin for Screenshots
#
# Save screenshots on certain events


class Screenshot(object):

    def apply_ui(self):
        self.result_detail_enabled = self.checkResultDetailEnable.GetValue()
        self.miiverse_drawing_enabled = self.checkMiiverseDrawingEnable.GetValue()
        self.dir = self.editDir.GetValue()

    def refresh_ui(self):
        self._internal_update = True
        self.checkResultDetailEnable.SetValue(self.result_detail_enabled)
        self.checkMiiverseDrawingEnable.SetValue(self.miiverse_drawing_enabled)

        if not self.dir is None:
            self.editDir.SetValue(self.dir)
        else:
            self.editDir.SetValue('')

    def on_config_reset(self, context=None):
        self.result_detail_enabled = False
        self.miiverse_drawing_enabled = False
        self.dir = os.path.join(os.getcwd(), 'screenshots')

    def on_config_load_from_context(self, context):
        self.on_config_reset(context)
        try:
            conf = context['config']['screenshot']
        except:
            conf = {}

        if 'ResultDetailEnable' in conf:
            self.result_detail_enabled = conf['ResultDetailEnable']

        if 'MiiverseDrawingEnable' in conf:
            self.miiverse_drawing_enabled = conf['MiiverseDrawingEnable']

        if 'Dir' in conf:
            self.dir = conf['Dir']

        self.refresh_ui()
        return True

    def on_config_save_to_context(self, context):
        context['config']['screenshot'] = {
            'ResultDetailEnable': self.result_detail_enabled,
            'MiiveseDrawingEnable': self.miiverse_drawing_enabled,
            'Dir': self.dir,
        }

    def on_config_apply(self, context):
        self.apply_ui()

    def on_option_tab_create(self, notebook):
        self.panel = wx.Panel(notebook, wx.ID_ANY)
        self.panel_name = _('Screenshot')
        self.layout = wx.BoxSizer(wx.VERTICAL)
        self.panel.SetSizer(self.layout)
        self.checkResultDetailEnable = wx.CheckBox(
            self.panel, wx.ID_ANY, _('Save screenshots of game results'))
        self.checkMiiverseDrawingEnable = wx.CheckBox(
            self.panel, wx.ID_ANY, _('Save drawings in Inkopolis'))
        self.editDir = wx.TextCtrl(self.panel, wx.ID_ANY, u'hoge')

        self.layout.Add(wx.StaticText(
            self.panel, wx.ID_ANY, _('Folder to save screenshots')))
        self.layout.Add(self.editDir, flag=wx.EXPAND)
        self.layout.Add(self.checkResultDetailEnable)
        self.layout.Add(self.checkMiiverseDrawingEnable)

        self.panel.SetSizer(self.layout)

    def save_drawing(self, context):
        x1 = 241
        x2 = x1 + 367
        y1 = 528
        y2 = y1 + 142

        drawing = context['engine']['frame'][y1:y2, x1:x2, :]

        timestr = time.strftime("%Y%m%d_%H%M%S",
                                time.localtime(IkaUtils.getTime(context)))
        destfile = os.path.join(self.dir, 'miiverse_%s.png' % timestr)

        IkaUtils.writeScreenshot(destfile, drawing)
        print(_('Saved a screenshot %s') % destfile)

    ##
    # on_result_detail_still Hook
    # @param self      The Object Pointer
    # @param context   IkaLog context
    #
    def on_result_detail_still(self, context):
        timestr = time.strftime("%Y%m%d_%H%M%S",
                                time.localtime(IkaUtils.getTime(context)))
        destfile = os.path.join(self.dir, 'ikabattle_%s.png' % timestr)

        IkaUtils.writeScreenshot(destfile, context['engine']['frame'])
        print(_('Saved a screenshot %s') % destfile)

    def on_key_press(self, context, key):
        if not (key == 0x53 or key == 0x73):
            return False

        if PlazaUserStat().match(context):
            self.save_drawing(context)

    ##
    # Constructor
    # @param self         The Object Pointer.
    # @param dir          Destionation directory (Relative path, or absolute path)
    #
    def __init__(self, dest_dir=None):
        self.result_detail_enabled = (not dest_dir is None)
        self.miiverse_drawing_enabled = False
        self.dir = dest_dir
