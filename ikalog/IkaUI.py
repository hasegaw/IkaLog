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

import yaml

from .engine import *
from .outputs.console import *
from .outputs.csv import *
from .outputs.json import *
from .outputs.screenshot import *
from .outputs.slack import *
from .outputs.twitter import *
from .outputs.videorecorder import *

from .IkaPanel_Preview import *
from .IkaPanel_Timeline import *
from .IkaPanel_Options import *

from .IkaUtils import *


class IkaLogGUI:

    def onNextFrame(self, context):
        # This IkaEngine thread a bit, so that GUI thread can process events.
        time.sleep(0.01)

    def OnOptionsApplyClick(self, sender):
        engine.callPlugins('onConfigApply', debug=True)
        engine.callPlugins('onConfigSaveToContext', debug=True)
        self.saveCurrentConfig(engine.context)

    def OnOptionsResetClick(self, sender):
        engine.callPlugins('onConfigLoadFromContext', debug=True)
        engine.callPlugins('onConfigReset', debug=True)

    def OnOptionsLoadDefaultClick(self, sender):
        r = wx.MessageDialog(None, 'All of IkaLog config will be reset. Are you sure to load default?', 'Confirmation',
                             wx.YES_NO | wx.NO_DEFAULT | wx.ICON_QUESTION).ShowModal()

        if r != wx.ID_YES:
            return

        engine.callPlugins('onConfigReset', debug=True)
        engine.callPlugins('onConfigSaveToContext', debug=True)
        self.saveCurrentConfig(engine.context)

    # 現在の設定値をYAMLファイルからインポート
    #
    def loadConfig(self, context, filename='IkaConfig.yaml'):
        try:
            yaml_file = open(filename, 'r')
            engine.context['config'] = yaml.load(yaml_file)
            yaml_file.close()
        except:
            pass

    # 現在の設定値をYAMLファイルにエクスポート
    #
    def saveCurrentConfig(self, context, filename='IkaConfig.yaml'):
        yaml_file = open(filename, 'w')
        yaml_file.write(yaml.dump(context['config']))
        yaml_file.close

    # パネル切り替え時の処理
    #
    def switchToPanel(self, activeButton):

        for button in [self.buttonPreview, self.buttonLastResult, self.buttonTimeline, self.buttonOptions]:
            panel = {
                self.buttonPreview: self.preview,
                self.buttonLastResult: self.lastResult,
                self.buttonTimeline: self.timeline,
                self.buttonOptions: self.options,
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

    def OnSwitchPanel(self, event):
        activeButton = event.GetEventObject()
        self.switchToPanel(activeButton)

    def UpdateEnableButton(self):
        color = '#00A000' if self.enable else '#C0C0C0'
        label = 'Stop' if self.enable else 'Start'
        self.buttonEnable.SetBackgroundColour(color)
        self.buttonEnable.SetLabel(label)

    def setEnable(self, enable):
        self.enable = enable
        engine.pause(not enable)
        self.UpdateEnableButton()

    def OnEnableButtonClick(self, event):
        self.setEnable(not self.enable)

    def OnClose(self, event):
        engine.stop()
        while engineThread.isAlive():
            time.sleep(0.5)
        self.frame.Destroy()

    def CreateButtonsUI(self):
        panel = self.frame
        self.buttonEnable = wx.Button(panel, wx.ID_ANY, u'Enable')
        self.buttonPreview = wx.Button(panel, wx.ID_ANY, u'Preview')
        self.buttonTimeline = wx.Button(panel, wx.ID_ANY, u'Timeline')
        self.buttonLastResult = wx.Button(panel, wx.ID_ANY, u'Last Result')
        self.buttonOptions = wx.Button(panel, wx.ID_ANY, u'Options')
        self.buttonDebugLog = wx.Button(panel, wx.ID_ANY, u'Debug Log')

        self.buttonsLayout = wx.BoxSizer(wx.HORIZONTAL)
        self.buttonsLayout.Add(self.buttonEnable)
        self.buttonsLayout.Add(self.buttonPreview)
        self.buttonsLayout.Add(self.buttonTimeline)
        self.buttonsLayout.Add(self.buttonLastResult)
        self.buttonsLayout.Add(self.buttonOptions)
        self.buttonsLayout.Add(self.buttonDebugLog)

        self.buttonPreview.Bind(wx.EVT_BUTTON, self.OnSwitchPanel)
        self.buttonLastResult.Bind(wx.EVT_BUTTON, self.OnSwitchPanel)
        self.buttonTimeline.Bind(wx.EVT_BUTTON, self.OnSwitchPanel)
        self.buttonOptions.Bind(wx.EVT_BUTTON, self.OnSwitchPanel)

    def __init__(self):
        self.frame = wx.Frame(None, wx.ID_ANY, "IkaLog GUI", size=(700, 500))

        self.layout = wx.BoxSizer(wx.VERTICAL)

        self.CreateButtonsUI()
        self.layout.Add(self.buttonsLayout)

        self.preview = PreviewPanel(self.frame, size=(640, 360))
        self.lastResult = LastResultPanel(self.frame, size=(640, 360))
        self.timeline = TimelinePanel(self.frame, size=(640, 200))
        self.options = OptionsPanel(self.frame, size=(640, 500))

        self.layout.Add(self.lastResult, flag=wx.EXPAND)
        self.layout.Add(self.preview, flag=wx.EXPAND)
        self.layout.Add(self.options, flag=wx.EXPAND)
        self.layout.Add(self.timeline, flag=wx.EXPAND)

        self.frame.SetSizer(self.layout)

        # Frame events
        self.frame.Bind(wx.EVT_CLOSE, self.OnClose)
        self.buttonEnable.Bind(wx.EVT_BUTTON, self.OnEnableButtonClick)

        # Set event handlers for options tab
        self.options.Bind('optionsApply', self.OnOptionsApplyClick)
        self.options.Bind('optionsReset', self.OnOptionsResetClick)
        self.options.Bind('optionsLoadDefault', self.OnOptionsLoadDefaultClick)

        self.switchToPanel(self.buttonPreview)

        # Ready.
        self.frame.Show()


def engineThread_func():
    IkaUtils.dprint('IkaEngine thread started')
    engine.run()
    IkaUtils.dprint('IkaEngine thread terminated')

if __name__ == "__main__":
    application = wx.App()
    inputPlugin = cvcapture()
    gui = IkaLogGUI()
    inputPlugin.onOptionTabCreate(gui.options.notebookOptions)
    gui.frame.Show()
    engine = IkaEngine()

    engine.setCapture(inputPlugin)
    plugins = []

    # とりあえずデバッグ用にコンソールプラグイン
    plugins.append(IkaOutput_Console())

    # 各パネルをプラグインしてイベントを受信する
    plugins.append(gui.preview)
    plugins.append(gui.lastResult)
    plugins.append(gui.timeline)

    # 設定画面を持つ input plugin もイベントを受信する
    plugins.append(inputPlugin)

    # UI 自体もイベントを受信
    plugins.append(gui)

    # 設定画面を持つ各種 Output Plugin
    # -> 設定画面の生成とプラグインリストへの登録
    for plugin in [
            IkaOutput_CSV(),
            # IkaOutput_Fluentd(),
            IkaOutput_JSON(),
            # IkaOutput_Hue(),
            IkaOutput_OBS(),
            IkaOutput_Twitter(),
            IkaOutput_Screenshot(),
            IkaOutput_Slack(),
    ]:
        print('Initializing %s' % plugin)
        plugin.onOptionTabCreate(gui.options.notebookOptions)
        plugins.append(plugin)

    # プラグインリストを登録
    engine.setPlugins(plugins)

    # IkaLog GUI 起動時にキャプチャが enable 状態かどうか
    gui.setEnable(True)

    # Loading config
    engine.callPlugins('onConfigReset', debug=True)
    gui.loadConfig(engine.context)
    engine.callPlugins('onConfigLoadFromContext', debug=True)

    engineThread = threading.Thread(target=engineThread_func)
    engineThread.start()
    application.MainLoop()
