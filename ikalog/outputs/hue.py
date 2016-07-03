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

import traceback
import math

from ikalog.utils import *



# Needed in GUI mode
try:
    import wx
except:
    pass

# IkaOutput_Hue: "Cameleon" Phillips Hue Lights.
#


class Hue(object):

    def apply_ui(self):
        self.enabled = self.checkEnable.GetValue()
        self.editHost = self.editHueHost.GetValue()
        self.dir = self.editHueUsername.GetValue()

    def refresh_ui(self):
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

    def on_config_reset(self, context=None):
        self.enabled = False
        self.hueHost = ''
        self.hueUsername = ''

    def on_config_load_from_context(self, context):
        self.on_config_reset(context)
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

        self.refresh_ui()
        return True

    def on_config_save_to_context(self, context):
        context['config']['hue'] = {
            'Enable': self.enabled,
            'HueHost': self.hueHost,
            'HueUsername': self.hueUsername,
        }

    def on_config_apply(self, context):
        self.apply_ui()

    def on_option_tab_create(self, notebook):
        self.panel = wx.Panel(notebook, wx.ID_ANY, size=(640, 360))
        self.panel_name = 'Hue'
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

    # enhance_color and rgb2xy is imported from:
    # https://gist.githubusercontent.com/error454/6b94c46d1f7512ffe5ee/raw/73b190ce256c3d8dd540cc34e6dae43848cbce4c/gistfile1.py

    # All the rights belongs to the author.
    def enhance_color(self, normalized):
        if normalized > 0.04045:
            return math.pow((normalized + 0.055) / (1.0 + 0.055), 2.4)
        else:
            return normalized / 12.92

    def rgb2xy(self, r, g, b):
        r_norm = r / 255.0
        g_norm = g / 255.0
        b_norm = b / 255.0

        r_final = self.enhance_color(r_norm)
        g_final = self.enhance_color(g_norm)
        b_final = self.enhance_color(b_norm)

        x = r_final * 0.649926 + g_final * 0.103455 + b_final * 0.197109
        y = r_final * 0.234327 + g_final * 0.743075 + b_final * 0.022598
        z = r_final * 0.000000 + g_final * 0.053077 + b_final * 1.035763

        if x + y + z == 0:
            return (0, 0)
        else:
            x_final = x / (x + y + z)
            y_final = y / (x + y + z)

            return (x_final, y_final)

    def light_team_color(self, context):
        if not ('team_color_bgr' in context['game']):
            return

        if self.hue_bridge is None:
            return

        team1 = context['game']['team_color_bgr'][0]
        team2 = context['game']['team_color_bgr'][1]

        # print(team1, team2)

        c1 = self.rgb2xy(team1[2], team1[1], team1[0])
        c2 = self.rgb2xy(team2[2], team2[1], team2[0])

        b1 = (team1[2] * 3 + team1[0] + team1[1] * 3) / 6 / 2
        b2 = (team2[2] * 3 + team2[0] + team2[1] * 3) / 6 / 2

        self.hue_bridge.lights(1, 'state', xy=c1, bri=255, sat=255)
        self.hue_bridge.lights(2, 'state', xy=c2, bri=255, sat=255)

    def on_frame_next(self, context):
        if context['engine']['inGame']:
            self.light_team_color(context)

    def check_import(self):
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

        self.check_import()

        import qhue
        try:
            self.hue_bridge = qhue.Bridge(host, user)
        except:
            IkaUtils.dprint('%s: Exception.' % self)
            IkaUtils.dprint(traceback.format_exc())

if __name__ == "__main__":
    obj = Hue(host='192.168.44.87', user='newdeveloper')

    context = {
        'game': {
            'inGame': True,
            'color': [[255, 0, 0], [0, 255, 0]],
        }
    }

    obj.light_team_color(context)
