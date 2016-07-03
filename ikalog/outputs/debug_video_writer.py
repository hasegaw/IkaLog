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
import sys
import threading
import time

import numpy as np
import cv2

from ikalog.utils import *

_ = Localization.gettext_translation('flight_recorder', fallback=True).gettext

# Needed in GUI mode
try:
    import wx
except:
    pass

# IkaLog Output Plugin: Write debug logs.


class DebugVideoWriter(object):

    def generate_mp4_filename(self):
        timestr = time.strftime("%Y%m%d_%H%M%S", time.localtime())
        destfile = os.path.join(self.dir, 'ikalog_debug_%s.avi' % timestr)
        return destfile

    def start_recording(self, filename=None):
        self.lock.acquire()

        if filename is None:
            filename = self.generate_mp4_filename()

        fps = 2
        capture_size = (1280, 720)
        if IkaUtils.isWindows():
            fourcc = cv2.VideoWriter_fourcc(
                'M', 'J', 'P', 'G')
        else:
            fourcc = cv2.VideoWriter_fourcc(
                'm', 'p', '4', 'v')  # note the lower case

        print('opening record file %s ....' % filename)
        self.movie_writer = cv2.VideoWriter()
        success = self.movie_writer.open(
            filename, fourcc, fps, capture_size, True)
        self._recording = True
        print('ok, started recording')

        self.lock.release()

    def stop_recording(self):
        self.lock.acquire()

        if not self._recording:
            self.lock.release()
            return None

        print('stopped recording')
        self.movie_writer = None
        self._recording = False

        self.lock.release()

    def on_debug_read_next_frame(self, context):
        self.lock.acquire()

        if self._recording:
            self.movie_writer.write(context['engine']['frame'])
        else:
            self.movie_out = None

        self.lock.release()

    def on_config_apply(self, context):
        self.dir = self.edit_dir.GetValue()

    def refresh_ui(self):
        if self.dir is None:
            self.edit_dir.SetValue('')
        else:
            self.edit_dir.SetValue(self.dir)

    def on_button_record_start_click(self, event):
        self.start_recording()

    def on_button_record_stop_click(self, event):
        self.stop_recording()

    def on_option_tab_create(self, notebook):
        self.panel = wx.Panel(notebook, wx.ID_ANY)
        self.panel_name = _('Flight recorder')
        self.layout = wx.BoxSizer(wx.VERTICAL)
        self.panel.SetSizer(self.layout)

        self.edit_dir = wx.TextCtrl(self.panel, wx.ID_ANY, 'hoge')
        self.button_record_start = wx.Button(self.panel, wx.ID_ANY, _('Start recording'))
        self.button_record_stop = wx.Button(self.panel, wx.ID_ANY, _('Stop recording'))

        self.layout.Add(wx.StaticText(
            self.panel, wx.ID_ANY, _('Flight recorder for IkaLog video recognition problems.')))

        self.layout.Add(wx.StaticText(
            self.panel, wx.ID_ANY, _('Output Folder')))

        self.layout.Add(self.edit_dir, flag=wx.EXPAND)
        self.layout.Add(self.button_record_start)
        self.layout.Add(self.button_record_stop)

        self.panel.SetSizer(self.layout)

        self.refresh_ui()

        self.button_record_start.Bind(wx.EVT_BUTTON, self.on_button_record_start_click)
        self.button_record_stop.Bind(wx.EVT_BUTTON, self.on_button_record_stop_click)

    def on_key_press(self, context, key):
        if key == ord('v'):
            if self._recording:
                self.stop_recording()
            else:
                self.start_recording()

    def __init__(self, dir='debug_videos/'):
        self._recording = False
        self.dir = dir
        self.lock = threading.Lock()
