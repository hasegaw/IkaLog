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
import os
import threading

import wx
import yaml

from ikalog.engine import *
from ikalog import outputs
from ikalog.ui.events import *
from ikalog.ui.panel import *
from ikalog.ui import VideoCapture
from ikalog.utils import *

_ = Localization.gettext_translation('IkaUI', fallback=True).gettext

class IkaLogGUI(object):

    def on_next_frame(self, context):
        # This IkaEngine thread a bit, so that GUI thread can process events.
        time.sleep(0.01)

    def on_options_apply_click(self, sender):
        self.engine.call_plugins('on_config_apply', debug=True)
        self.engine.call_plugins('on_config_save_to_context', debug=True)
        self.save_current_config(self.engine.context)

    def on_options_reset_click(self, sender):
        self.engine.call_plugins('on_config_load_from_context', debug=True)
        self.engine.call_plugins('on_config_reset', debug=True)

    def on_options_load_default_click(self, sender):
        r = wx.MessageDialog(
            None,
            _('IkaLog preferences will be reset to default. Continue?'),
            _('Confirm'),
            wx.YES_NO | wx.NO_DEFAULT | wx.ICON_QUESTION
        ).ShowModal()

        if r != wx.ID_YES:
            return

        self.engine.call_plugins('on_config_reset', debug=True)
        self.engine.call_plugins('on_config_save_to_context', debug=True)
        self.save_current_config(self.engine.context)

    # 現在の設定値をYAMLファイルからインポート
    #
    def load_config(self, context, filename='IkaConfig.yaml'):
        try:
            yaml_file = open(filename, 'r')
            self.engine.context['config'] = yaml.load(yaml_file)
            yaml_file.close()
        except:
            pass

    # 現在の設定値をYAMLファイルにエクスポート
    #
    def save_current_config(self, context, filename='IkaConfig.yaml'):
        yaml_file = open(filename, 'w')
        yaml_file.write(yaml.dump(context['config']))
        yaml_file.close

    # パネル切り替え時の処理
    #
    def switch_to_panel(self, activeButton):

        for button in [self.button_preview, self.button_last_result, self.button_timeline, self.button_options]:
            panel = {
                self.button_preview: self.preview,
                self.button_last_result: self.last_result,
                self.button_timeline: self.timeline,
                self.button_options: self.options,
            }[button]

            if button == activeButton:
                button.Disable()
                panel.Show()
                # print('%s is shown' % panel)
            else:
                button.Enable()
                panel.Hide()
                # print('%s is hidden' % panel)

        # リサイズイベントが発生しないと画面レイアウトが正しくならないので
        try:
            # Project Phoenix
            self.layout.Layout()
        except:
            # If it doesn't work... for old wxPython
            w, h = self.frame.GetClientSizeTuple()
            self.frame.SetSizeWH(w, h)

    def on_switch_panel(self, event):
        active_button = event.GetEventObject()
        self.switch_to_panel(active_button)

    def update_enable_button(self):
        color = '#00A000' if self.enable else '#C0C0C0'
        label = _('Stop') if self.enable else _('Start')
        self.button_enable.SetBackgroundColour(color)
        self.button_enable.SetLabel(label)

    def set_enable(self, enable):
        self.enable = enable
        self.engine.pause(not enable)
        self.update_enable_button()

    def on_enable_button_click(self, event):
        self.set_enable(not self.enable)

    def on_close(self, event):
        self.engine.stop()
        while self.engine_thread.is_alive():
            time.sleep(0.5)
        self.frame.Destroy()

    def on_input_file_added(self, event):
        self.engine.put_source_file(event.input_file)

    def on_input_initialized(self, event):
        self.engine.reset_capture()
        # Propagate the event as the top level event.
        wx.PostEvent(self.frame, event)

    def create_buttons_ui(self):
        panel = self.frame
        self.button_enable = wx.Button(panel, wx.ID_ANY, _('Enable'))
        self.button_preview = wx.Button(panel, wx.ID_ANY, _('Preview'))
        self.button_timeline = wx.Button(panel, wx.ID_ANY, _('Timeline'))
        self.button_last_result = wx.Button(panel, wx.ID_ANY, _('Last Result'))
        self.button_options = wx.Button(panel, wx.ID_ANY, _('Options'))
        self.button_debug_log = wx.Button(panel, wx.ID_ANY, _('Debug Log'))

        self.buttons_layout = wx.BoxSizer(wx.HORIZONTAL)
        self.buttons_layout.Add(self.button_enable)
        self.buttons_layout.Add(self.button_preview)
        self.buttons_layout.Add(self.button_timeline)
        self.buttons_layout.Add(self.button_last_result)
        self.buttons_layout.Add(self.button_options)
        self.buttons_layout.Add(self.button_debug_log)

        self.button_preview.Bind(wx.EVT_BUTTON, self.on_switch_panel)
        self.button_last_result.Bind(wx.EVT_BUTTON, self.on_switch_panel)
        self.button_timeline.Bind(wx.EVT_BUTTON, self.on_switch_panel)
        self.button_options.Bind(wx.EVT_BUTTON, self.on_switch_panel)

    def engine_thread_func(self):
        IkaUtils.dprint('IkaEngine thread started')
        self.engine.run()
        IkaUtils.dprint('IkaEngine thread terminated')

    def create_engine(self):
        self.engine = IkaEngine(keep_alive=True)
        return self.engine

    def start_engine(self):
        self.engine_thread = threading.Thread(target=self.engine_thread_func)
        self.engine_thread.daemon = True
        self.engine_thread.start()

    def __init__(self, capture):
        self.capture = capture
        self.frame = wx.Frame(None, wx.ID_ANY, "IkaLog GUI", size=(700, 500))

        self.layout = wx.BoxSizer(wx.VERTICAL)

        self.create_buttons_ui()
        self.layout.Add(self.buttons_layout)

        self.preview = PreviewPanel(self.frame, size=(640, 420))
        self.preview.Bind(EVT_INPUT_FILE_ADDED, self.on_input_file_added)

        self.last_result = LastResultPanel(self.frame, size=(640, 360))
        self.timeline = TimelinePanel(self.frame, size=(640, 200))
        self.options = OptionsPanel(self.frame)

        self.capture.on_option_tab_create(self.options.notebookOptions)
        self.capture.panel.Bind(EVT_INPUT_INITIALIZED,
                                self.on_input_initialized)

        self.layout.Add(self.last_result, flag=wx.EXPAND)
        self.layout.Add(self.preview, flag=wx.EXPAND)
        self.layout.Add(self.options, flag=wx.EXPAND)
        self.layout.Add(self.timeline, flag=wx.EXPAND)

        self.frame.SetSizer(self.layout)

        # Frame events
        self.frame.Bind(wx.EVT_CLOSE, self.on_close)
        self.button_enable.Bind(wx.EVT_BUTTON, self.on_enable_button_click)

        # Set event handlers for options tab
        self.options.Bind('optionsApply', self.on_options_apply_click)
        self.options.Bind('optionsReset', self.on_options_reset_click)
        self.options.Bind('optionsLoadDefault',
                          self.on_options_load_default_click)

        self.switch_to_panel(self.button_preview)

        # Ready.
        self.frame.Show()
