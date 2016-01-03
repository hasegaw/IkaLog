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
import threading

import wx
import yaml

from ikalog.engine import *
from ikalog import outputs
from ikalog.ui.panel import *
from ikalog.ui import VideoCapture
from ikalog.utils import *


class IkaLogGUI(object):

    def on_next_frame(self, context):
        # This IkaEngine thread a bit, so that GUI thread can process events.
        time.sleep(0.01)

    def on_options_apply_click(self, sender):
        engine.call_plugins('on_config_apply', debug=True)
        engine.call_plugins('on_config_save_to_context', debug=True)
        self.save_current_config(engine.context)

    def on_options_reset_click(self, sender):
        engine.call_plugins('on_config_load_from_context', debug=True)
        engine.call_plugins('on_config_reset', debug=True)

    def on_options_load_default_click(self, sender):
        r = wx.MessageDialog(None, 'All of IkaLog config will be reset. Are you sure to load default?', 'Confirmation',
                             wx.YES_NO | wx.NO_DEFAULT | wx.ICON_QUESTION).ShowModal()

        if r != wx.ID_YES:
            return

        engine.call_plugins('on_config_reset', debug=True)
        engine.call_plugins('on_config_save_to_context', debug=True)
        self.save_current_config(engine.context)

    # 現在の設定値をYAMLファイルからインポート
    #
    def load_config(self, context, filename='IkaConfig.yaml'):
        try:
            yaml_file = open(filename, 'r')
            engine.context['config'] = yaml.load(yaml_file)
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
                print('%s is shown' % panel)
            else:
                button.Enable()
                panel.Hide()
                print('%s is hidden' % panel)

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
        label = 'Stop' if self.enable else 'Start'
        self.button_enable.SetBackgroundColour(color)
        self.button_enable.SetLabel(label)

    def set_enable(self, enable):
        self.enable = enable
        engine.pause(not enable)
        self.update_enable_button()

    def on_enable_button_click(self, event):
        self.set_enable(not self.enable)

    def on_close(self, event):
        engine.stop()
        while engine_thread.is_alive():
            time.sleep(0.5)
        self.frame.Destroy()

    def create_buttons_ui(self):
        panel = self.frame
        self.button_enable = wx.Button(panel, wx.ID_ANY, u'Enable')
        self.button_preview = wx.Button(panel, wx.ID_ANY, u'Preview')
        self.button_timeline = wx.Button(panel, wx.ID_ANY, u'Timeline')
        self.button_last_result = wx.Button(panel, wx.ID_ANY, u'Last Result')
        self.button_options = wx.Button(panel, wx.ID_ANY, u'Options')
        self.button_debug_log = wx.Button(panel, wx.ID_ANY, u'Debug Log')

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

    def __init__(self):
        self.frame = wx.Frame(None, wx.ID_ANY, "IkaLog GUI", size=(700, 500))

        self.layout = wx.BoxSizer(wx.VERTICAL)

        self.create_buttons_ui()
        self.layout.Add(self.buttons_layout)

        self.preview = PreviewPanel(self.frame, size=(640, 360))
        self.last_result = LastResultPanel(self.frame, size=(640, 360))
        self.timeline = TimelinePanel(self.frame, size=(640, 200))
        self.options = OptionsPanel(self.frame, size=(640, 500))

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


def engine_thread_func():
    IkaUtils.dprint('IkaEngine thread started')
    engine.run()
    IkaUtils.dprint('IkaEngine thread terminated')

if __name__ == "__main__":
    application = wx.App()
    input_plugin = VideoCapture()
    gui = IkaLogGUI()
    input_plugin.on_option_tab_create(gui.options.notebookOptions)
    gui.frame.Show()

    engine = IkaEngine()
    engine.close_session_at_eof = True
    engine.set_capture(input_plugin)
    plugins = []

    # とりあえずデバッグ用にコンソールプラグイン
    plugins.append(outputs.Console())

    # 各パネルをプラグインしてイベントを受信する
    plugins.append(gui.preview)
    plugins.append(gui.last_result)
    plugins.append(gui.timeline)

    # 設定画面を持つ input plugin もイベントを受信する
    plugins.append(input_plugin)

    # UI 自体もイベントを受信
    plugins.append(gui)

    # 設定画面を持つ各種 Output Plugin
    # -> 設定画面の生成とプラグインリストへの登録
    for plugin in [
            outputs.CSV(),
            # outputs.Fluentd(),
            outputs.JSON(),
            # outputs.Hue(),
            outputs.OBS(),
            outputs.Twitter(),
            outputs.Screenshot(),
            outputs.Boyomi(),
            outputs.Slack(),
            outputs.StatInk(),
            outputs.DebugVideoWriter(),
            outputs.WebSocketServer(),
    ]:
        print('Initializing %s' % plugin)
        plugin.on_option_tab_create(gui.options.notebookOptions)
        plugins.append(plugin)

    # 本当に困ったときのデバッグログ増加モード
    if 'IKALOG_DEBUG' in os.environ:
        plugins.append(outputs.DebugLog())

    # プラグインリストを登録
    engine.set_plugins(plugins)

    # IkaLog GUI 起動時にキャプチャが enable 状態かどうか
    gui.set_enable(True)

    # Loading config
    engine.call_plugins('on_config_reset', debug=True)
    gui.load_config(engine.context)
    engine.call_plugins('on_config_load_from_context', debug=True)

    engine_thread = threading.Thread(target=engine_thread_func)
    engine_thread.daemon = True
    engine_thread.start()
    application.MainLoop()
