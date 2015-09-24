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

import wx


class TimelinePanel(wx.Panel):
    margin_dots = 30
    max_game_period = 60 * 5  # in seconds
    game_period = max_game_period
    context = None

    def onFrameNext(self, context):
        if self.context is None:
            self.context = context
        self.Refresh()

    def rescaleX(self, context):
        self.game_period = self.max_game_period
        if not 'livesTrack' in context['game']:
            return

        # 横幅を確定する
        l = len(self.context['game']['livesTrack'])

        if l < 2:
            return

        t1 = self.context['game']['livesTrack'][0][0]
        t2 = self.context['game']['livesTrack'][l - 1][0]
        t = int((t2 - t1) / 1000 + 0.999)
        self.game_period = t

    def drawLives(self, context):
        if not 'livesTrack' in context['game']:
            return False

        if len(context['game']['livesTrack']) < 1:
            return False

        time_origin = context['game']['livesTrack'][0][0]

        last_xPos = None
        last_yPos = None
        for sample in context['game']['livesTrack']:
            msec = sample[0] - time_origin
            team1_lives = sample[1]
            team2_lives = sample[2]

            xPos = 0 if msec == 0 else int(
                ((msec * 1.0) / (self.game_period * 1000.0)) * self.gw)

            # team1
            y1 = 0
            for life in team1_lives:
                y1 = y1 + {True: 1, False: 0}[life]

            y2 = 0
            for life in team2_lives:
                y2 = y2 + {True: 1, False: 0}[life]

            if y1 == 0 and y2 == 0:
                # 全員相打ちクソワロタ
                h1 = 0
                h2 = 0
            elif y1 == 0:
                h1 = 0
                h2 = self.gh
            elif y2 == 0:
                h1 = self.gh
                h2 = 0
            else:
                h1 = (y1 * 1.0) / ((y1 + y2) * 1.0) * self.gh
                h2 = self.gh - h1

#			h1 = y1 * 1.0 * (self.gh / 8)
#			h2 = y2 * 1.0 * (self.gh / 8)

            if not last_xPos is None:
                self.dc.SetPen(wx.Pen(wx.GREEN, 1))
                self.dc.SetBrush(wx.Brush('green'))
                self.dc.DrawRectangle(
                    self.margin_dots + last_xPos, self.margin_dots, xPos - last_xPos, h2)

                self.dc.SetPen(wx.Pen(wx.YELLOW, 1))
                self.dc.SetBrush(wx.Brush('yellow'))
                self.dc.DrawRectangle(
                    self.margin_dots + last_xPos, self.margin_dots + self.gh - h1, xPos - last_xPos,  h1)
            last_xPos = xPos

    def drawTower(self, context):
        if not 'towerTrack' in context['game']:
            #print('drawTower: no track data')
            return False

        if len(context['game']['towerTrack']) < 1:
            #print('drawTower: no track data 2')
            return False

        time_origin = context['game']['towerTrack'][0][0]

        self.dc.SetPen(wx.Pen(wx.RED, 3))

        last_xPos = None
        last_yPos = None
        for sample in context['game']['towerTrack']:
            msec = sample[0] - time_origin
            vals = sample[1]

            xPos = 0 if msec == 0 else int(
                msec * self.gw / (self.game_period * 1000.0))
            yPos = 0 if vals['pos'] == 0 else vals['pos'] * (self.gh / 2) / 100
            yPos = int(self.gh / 2 - yPos)
            if not last_yPos is None:
                self.dc.DrawLine(self.margin_dots + last_xPos, self.margin_dots +
                                 last_yPos, self.margin_dots + xPos, self.margin_dots + yPos)
            last_xPos = xPos
            last_yPos = yPos

    def drawGraphXaxis(self):
        for t in range(int(self.game_period / 60) + 2):
            x = int(self.gw * (t * 60) / self.game_period)
            if (x < self.gw):
                self.dc.SetPen(wx.Pen(wx.LIGHT_GREY,  2))
                self.dc.DrawLine(self.margin_dots + x, self.margin_dots,
                                 self.margin_dots + x, self.margin_dots + self.gh)

                s = '%d:00' % t
                self.dc.SetFont(wx.Font(8, wx.FONTFAMILY_DEFAULT,
                                        wx.FONTSTYLE_NORMAL, wx.FONTWEIGHT_NORMAL))
                self.dc.DrawText(s, self.margin_dots + x,
                                 self.margin_dots + self.gh)

            x = int(self.gw * (t * 60 + 30) / self.game_period)
            if (x < self.gw):
                self.dc.SetPen(wx.Pen(wx.LIGHT_GREY,  1))
                self.dc.DrawLine(self.margin_dots + x, self.margin_dots,
                                 self.margin_dots + x, self.margin_dots + self.gh)

                s = '%d:30' % t
                self.dc.SetFont(wx.Font(8, wx.FONTFAMILY_DEFAULT,
                                        wx.FONTSTYLE_NORMAL, wx.FONTWEIGHT_NORMAL))
                self.dc.DrawText(s, self.margin_dots + x,
                                 self.margin_dots + self.gh)

    def drawGraphFrame(self):
        self.dc.SetBackground(wx.Brush(wx.WHITE))
        self.dc.Clear()

    def drawGraphFinalize(self):
        self.dc.SetPen(wx.Pen(wx.BLACK, 3))
        self.dc.DrawLine(self.margin_dots, self.margin_dots,
                         self.margin_dots, self.margin_dots + self.gh)
        self.dc.DrawLine(self.margin_dots, self.margin_dots + self.gh,
                         self.margin_dots + self.gw, self.margin_dots + self.gh)

    def OnPaint(self, event):
        self.dc = wx.PaintDC(self)
        try:
            w, h = self.GetClientSizeTuple()
        except:
            w, h = self.GetClientSize()

        # グラフ描画サイズ (gw: 横幅, gh: 縦幅)
        # マージンを除いた実際の四角形のサイズ

        self.gw = float(w) - self.margin_dots * 2
        self.gh = float(h) - self.margin_dots * 2

        # デフォルトのペン、フォントのリファレンスを残しておく
        self.default_pen = self.dc.GetPen()
        self.default_font = self.dc.GetFont()

        self.drawGraphFrame()

        if self.context is None:
            # !!
            return

        self.rescaleX(self.context)
        self.drawLives(self.context)
        self.drawGraphXaxis()
        self.drawTower(self.context)

        self.drawGraphFinalize()

        self.dc.SetPen(self.default_pen)
        self.dc.SetFont(self.default_font)

        return

    def __init__(self, *args, **kwargs):
        self.latest_frame = None
        wx.Panel.__init__(self, *args, **kwargs)
        self.Bind(wx.EVT_PAINT, self.OnPaint)
#		self.Bind(wx.EVT_SIZE, self.OnResize)


if __name__ == "__main__":
    import sys
    import wx
    import pickle

    application = wx.App()
    frame = wx.Frame(None, wx.ID_ANY, 'Preview', size=(640, 360))
    timeline = TimelinePanel(frame, size=(640, 100))

    f = open('game.pickle', 'rb')
    timeline.context = {'game': pickle.load(f)}
    f.close()

    layout = wx.BoxSizer(wx.VERTICAL)
    layout.Add(timeline)

    frame.SetSizer(layout)
    frame.Show()
    application.MainLoop()
