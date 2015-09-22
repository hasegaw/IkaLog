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

# Needed in GUI mode
try:
    import wx
except:
    pass

import sys
import math
from IkaUtils import *

# Needed in GUI mode
try:
    import wx
except:
    pass

# IkaOutput_Hue: "Cameleon" Phillips Hue Lights.
#


class IkaOutput_Hue:

    def ApplyUI(self):
        self.enabled = self.checkEnable.GetValue()
        self.editHost = self.editHueHost.GetValue()
        self.dir = self.editHueUsername.GetValue()

    def RefreshUI(self):
        self._internal_update = True
        self.checkEnable.SetValue(self.enabled)

        if not self.hueHost is None:
            self.editHueHost.SetValue(self.hueHost)
        else:
            self.editHueHost.SetValue('')

        if not self.hueUsername is None:
            self.editHueUsername.SetValue(self.hueUsername)
        else:
            self.editHueUsername.SetValue('')

    def onConfigReset(self, context=None):
        self.enabled = False
        self.hueHost = ''
        self.hueUsername = ''

    def onConfigLoadFromContext(self, context):
        self.onConfigReset(context)
        try:
            conf = context['config']['hue']
        except:
            conf = {}

        if 'Enable' in conf:
            self.enabled = conf['Enable']

        if 'HueHost' in conf:
            self.hueHost = conf['HueHost']

        if 'HueHost' in conf:
            self.hueUsername = conf['HueUsername']

        self.RefreshUI()
        return True

    def onConfigSaveToContext(self, context):
        context['config']['hue'] = {
            'Enable': self.enabled,
            'HueHost': self.hueHost,
            'HueUsername': self.hueUsername,
        }

    def onConfigApply(self, context):
        self.ApplyUI()

    def onOptionTabCreate(self, notebook):
        self.panel = wx.Panel(notebook, wx.ID_ANY, size=(640, 360))
        self.page = notebook.InsertPage(0, self.panel, 'Hue')
        self.layout = wx.BoxSizer(wx.VERTICAL)
        self.panel.SetSizer(self.layout)
        self.checkEnable = wx.CheckBox(self.panel, wx.ID_ANY, u'Hue と連携')
        self.editHueHost = wx.TextCtrl(self.panel, wx.ID_ANY, u'hoge')
        self.editHueUsername = wx.TextCtrl(self.panel, wx.ID_ANY, u'hoge')

        try:
            layout = wx.GridSizer(2, 2)
        except:
            layout = wx.GridSizer(2)

        layout.Add(wx.StaticText(self.panel, wx.ID_ANY, u'ホスト'))
        layout.Add(self.editHueHost)
        layout.Add(wx.StaticText(self.panel, wx.ID_ANY, u'ユーザ'))
        layout.Add(self.editHueUsername)
        self.layout.Add(self.checkEnable)
        self.layout.Add(layout)

    # EnhanceColor and RGBtoXY is imported from:
    # https://gist.githubusercontent.com/error454/6b94c46d1f7512ffe5ee/raw/73b190ce256c3d8dd540cc34e6dae43848cbce4c/gistfile1.py

    # All the rights belongs to the author.
    def EnhanceColor(self, normalized):
        if normalized > 0.04045:
            return math.pow((normalized + 0.055) / (1.0 + 0.055), 2.4)
        else:
            return normalized / 12.92

    def RGBtoXY(self, r, g, b):
        rNorm = r / 255.0
        gNorm = g / 255.0
        bNorm = b / 255.0

        rFinal = self.EnhanceColor(rNorm)
        gFinal = self.EnhanceColor(gNorm)
        bFinal = self.EnhanceColor(bNorm)

        X = rFinal * 0.649926 + gFinal * 0.103455 + bFinal * 0.197109
        Y = rFinal * 0.234327 + gFinal * 0.743075 + bFinal * 0.022598
        Z = rFinal * 0.000000 + gFinal * 0.053077 + bFinal * 1.035763

        if X + Y + Z == 0:
            return (0, 0)
        else:
            xFinal = X / (X + Y + Z)
            yFinal = Y / (X + Y + Z)

            return (xFinal, yFinal)

    def lightTeamColor(self, context):
        team1 = context['game']['color'][0]
        team2 = context['game']['color'][1]

        # print(team1, team2)

        c1 = self.RGBtoXY(team1[2], team1[1], team1[0])
        c2 = self.RGBtoXY(team2[2], team2[1], team2[0])

        b1 = (team1[2] * 3 + team1[0] + team1[1] * 3) / 6 / 2
        b2 = (team2[2] * 3 + team2[0] + team2[1] * 3) / 6 / 2

        self.hue_bridge.lights(1, 'state', xy=c1, bri=255, sat=255)
        self.hue_bridge.lights(2, 'state', xy=c2, bri=255, sat=255)

    def onFrameNext(self, context):
        if context['engine']['inGame']:
            if ('color' in context['game']):
                self.lightTeamColor(context)

    def checkImport(self):
        try:
            import qhue
        except:
            print("モジュール qhue がロードできませんでした。 Hue 連携ができません。")
            #print("インストールするには以下のコマンドを利用してください。\n    pip install fluent-logger\n")

    ##
    # Constructor
    # @param self     The Object Pointer.
    # @param tag      tag
    # @param username Username of the player.
    # @param host     Fluentd host if Fluentd is on a different node
    # @param port     Fluentd port
    # @param username Name the bot use on Slack
    #
    def __init__(self, host=None, user=None):
        self.enabled = (not host is None)
        if not (host and user):
            self.hue_bridge = None
            return None

        checkImport()

        import qhue
        self.hue_bridge = qhue.Bridge(host, user)

if __name__ == "__main__":
    obj = IkaOutput_Hue(host='192.168.44.87', user='newdeveloper')

    context = {
        'game': {
            'inGame': True,
            'color': [[255, 0, 0], [0, 255, 0]],
        }
    }

    obj.lightTeamColor(context)
