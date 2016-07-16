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

import gettext

import wx
import wx.lib.scrolledpanel

import ikalog.outputs
from ikalog.ui.events import *
from ikalog.ui.panel import *
from ikalog.ui import VideoCapture
from ikalog.utils import *

_ = Localization.gettext_translation('IkaUI', fallback=True).gettext

class OptionsGUI(object):
    def __init__(self, ikalog_gui):
        self.ikalog_gui = ikalog_gui
        self.frame = None
        self._init_frame()

    def _init_frame(self):
        if self.frame:
            return

        self.frame = wx.Frame(
            self.ikalog_gui.frame, wx.ID_ANY, _("Options"), size=(640, 500))

        self.notebook = wx.Notebook(self.frame, wx.ID_ANY)

        # Apply button
        button_apply = wx.Button(self.frame, wx.ID_ANY, _(u'Apply'))

        # Use a bold font.
        apply_font = button_apply.GetFont()
        apply_font.SetWeight(wx.FONTWEIGHT_BOLD)
        button_apply.SetFont(apply_font)

        button_cancel = wx.Button(self.frame, wx.ID_ANY, _(u'Cancel'))
        button_load_default = wx.Button(
            self.frame, wx.ID_ANY, _(u'Load default'))

        buttons_sizer = wx.BoxSizer(wx.HORIZONTAL)
        buttons_sizer.Add(button_apply)
        buttons_sizer.Add(button_cancel)
        buttons_sizer.Add(button_load_default)

        top_sizer = wx.BoxSizer(wx.VERTICAL)
        top_sizer.Add(self.notebook)
        top_sizer.Add(buttons_sizer)

        self.frame.SetSizer(top_sizer)

        # Set event handlers for buttons.
        button_apply.Bind(wx.EVT_BUTTON, self.on_button_apply)
        button_cancel.Bind(wx.EVT_BUTTON, self.on_button_cancel)
        button_load_default.Bind(wx.EVT_BUTTON, self.on_button_load_default)

        outputs = [self.ikalog_gui.capture] + self.ikalog_gui.outputs
        self._init_outputs(outputs)

        # self.capture.panel is a part of self.frame. This Bind propagates
        # capture's source change to the preview.
        self.ikalog_gui.capture.panel.Bind(
            EVT_INPUT_INITIALIZED, self.ikalog_gui.on_input_initialized)

        # Refresh UI of each plugin.
        self.ikalog_gui.engine.call_plugins(
            'on_config_load_from_context', debug=True)

    def show(self):
        if not self.frame:
            self._init_frame()
        self.frame.Show()
        self.frame.Raise()

    def on_button_apply(self, event):
        self.ikalog_gui.on_options_apply(event)

    def on_button_cancel(self, event):
        self.ikalog_gui.on_options_cancel(event)

    def on_button_load_default(self, event):
        self.ikalog_gui.on_options_load_default(event)

    def _init_outputs(self, outputs):
        output_dict = {}
        for output in outputs:
            output_dict[output.__class__] = output

        # Keys for outputs in the main page.
        keys = [
            ikalog.ui.VideoCapture,
            ikalog.outputs.OBS,
            ikalog.outputs.StatInk,
            ikalog.outputs.Twitter
        ]
        # Keys for outputs combined into the misc tab.
        misc_keys = [
            ikalog.outputs.CSV,
            ikalog.outputs.JSON,
            ikalog.outputs.Screenshot,
            ikalog.outputs.Boyomi,
            ikalog.outputs.Slack,
            ikalog.outputs.WebSocketServer,
            ikalog.outputs.DebugVideoWriter,
        ]
        for key in output_dict.keys():
            if key in misc_keys:
                continue
            if key not in keys:
                keys.append(key)

        # Main tabs
        index = 0
        for key in keys:
            output = output_dict.get(key)
            if not output:
                continue

            output.on_option_tab_create(self.notebook)
            self.notebook.InsertPage(index, output.panel, output.panel_name)
            index += 1

        # Misc tab
        self.misc_panel = wx.lib.scrolledpanel.ScrolledPanel(
            self.notebook, wx.ID_ANY, size=(640, 360))
        self.misc_panel_sizer = wx.BoxSizer(wx.VERTICAL)
        default_font = self.misc_panel.GetFont()
        title_font = wx.Font(default_font.GetPointSize(),
                             wx.FONTFAMILY_DEFAULT,
                             wx.FONTSTYLE_NORMAL,
                             wx.FONTWEIGHT_BOLD)

        for key in misc_keys:
            output = output_dict.get(key)
            if not output:
                continue

            output.on_option_tab_create(self.misc_panel)
            title = wx.StaticText(self.misc_panel, wx.ID_ANY, output.panel_name)
            title.SetFont(title_font)
            self.misc_panel_sizer.Add(title)
            self.misc_panel_sizer.Add(
                output.panel, flag=wx.EXPAND | wx.ALL, border=10)
            self.misc_panel_sizer.Add((-1, 25))

        self.misc_panel.SetSizer(self.misc_panel_sizer)
        self.misc_panel.SetupScrolling()

        self.notebook.InsertPage(index, self.misc_panel, _('Misc.'))
