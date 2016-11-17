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

import copy
import os.path
import threading

import wx
import cv2

from ikalog.utils import Localization
from ikalog.ui.events import *

_ = Localization.gettext_translation('IkaUI', fallback=True).gettext

class FileDropTarget(wx.FileDropTarget):
    def __init__(self, observer):
        wx.FileDropTarget.__init__(self)
        self.observer = observer

    def OnDropFiles(self, x, y, filenames):
        self.observer.on_drop_files(x, y, filenames)
        return True

class InputFilePanel(wx.Panel):
    def __init__(self, *args, **kwargs):
        wx.Panel.__init__(self, *args, **kwargs)

        # This is used to determine if a file dialog is open or not.
        self.prev_file_path = ''

        # Textbox for input file
        self.text_ctrl = wx.TextCtrl(self, wx.ID_ANY, '')
        self.text_ctrl.Bind(wx.EVT_TEXT, self.on_text_input)
        self.button = wx.Button(self, wx.ID_ANY, _('Browse'))
        self.button.Bind(wx.EVT_BUTTON, self.on_button_click)

        # Drag and drop
        drop_target = FileDropTarget(self)
        self.text_ctrl.SetDropTarget(drop_target)

        top_sizer = wx.BoxSizer(wx.HORIZONTAL)
        top_sizer.Add(self.text_ctrl, proportion=1)
        top_sizer.Add(self.button)

        self.SetSizer(top_sizer)

    def should_open_file(self, file_path):
       return os.path.isfile(file_path) and self.prev_file_path != file_path

    def update_button_label(self):
        file_path = self.text_ctrl.GetValue()
        if self.should_open_file(file_path):
            self.button.SetLabel(_('Open'))
        else:
            self.button.SetLabel(_('Browse'))

    # wx event
    def on_text_input(self, event):
        self.update_button_label()

    # wx event
    def on_button_click(self, event):
        file_path = self.text_ctrl.GetValue()
        if self.should_open_file(file_path):
            evt = InputFileAddedEvent(input_file=file_path)
            wx.PostEvent(self, evt)
            self.prev_file_path = file_path
            self.update_button_label()
            return

        # file_path is invalid. Open a file dialog.
        file_dialog = wx.FileDialog(self, _('Select a video file'))
        if file_dialog.ShowModal() != wx.ID_OK:
            return
        file_path = file_dialog.GetPath()
        self.text_ctrl.SetValue(file_path)


    # Callback from wx.FileDropTarget.OnDropFiles
    def on_drop_files(self, x, y, filenames):
        if not filenames:
            return
        self.text_ctrl.SetValue(filenames[0])


class PreviewPanel(wx.Panel):

    def SetEventHandlerEnable(self, obj, enable):
        orig_state = obj.GetEvtHandlerEnabled()
        obj.SetEvtHandlerEnabled(enable)
        return orig_state


    # IkaLog event
    def on_amarec16x10_warning(self, context, params):
        self._amarec16x10_warning = params['enabled']

    # IkaLog event
    def on_show_preview(self, context):
        img = context['engine'].get('preview', context['engine']['frame'])
        if img is None:
            return False

        try:
            self.lock.acquire()

            self.latest_frame = cv2.resize(img, self.preview_size)
            self.refresh_at_next = True
        finally:
            self.lock.release()

    # wx event
    def on_input_initialized(self, event):
        self.show_header(event.source)

    # wx event
    def on_ikalog_pause(self, event):
        self._pause = event.pause
        self.draw_preview()

    # wx event
    def on_preview_click(self, event):
        evt = IkalogPauseEvent(pause=(not self._pause))
        wx.PostEvent(self, evt)

    # wx event
    def on_enter_preview(self, event):
        self._enter = True
        self.draw_preview()

    # wx event
    def on_leave_preview(self, event):
        self._enter = False
        self.draw_preview()

    # wx event
    def on_input_file_added(self, event):
        # Propagate the event to the upper level.
        wx.PostEvent(self, event)

    source_message = {
        'amarec': _('Capture through AmarecTV'),
        'dshow_capture': _('HDMI Video input (DirectShow, recommended)'),
        'opencv_capture': _('HDMI Video input (OpenCV driver)'),
        'screen': _('Realtime Capture from desktop'),
        'file': _('Read from pre-recorded video file (for testing)'),
    }
    def show_header(self, source):
        self.video_input_source_text.SetLabel(
            PreviewPanel.source_message.get(source, ''))
        self.show_input_file((source == 'file'))

    def show_input_file(self, show):
        self.input_file_panel.Show(show)
        self.Layout()

    def draw_preview(self):
        frame_rgb = None

        try:
            self.lock.acquire()

            if self.latest_frame is None:
                if self._prev_bmp:
                    dc.DrawBitmap(self._prev_bmp, 0, 0)
                return False

            width, height = self.preview_size
            frame_rgb = cv2.cvtColor(self.latest_frame, cv2.COLOR_BGR2RGB)
        finally:
            self.lock.release()

        if frame_rgb is None:
            return False

        bmp = wx.BitmapFromBuffer(width, height, frame_rgb)

        dc = wx.ClientDC(self.preview_panel)
        dc.DrawBitmap(bmp, 0, 0)
        self._prev_bmp = bmp

        if self._enter:
            ox = int(width / 2)
            oy = int(height / 2)
            if self._pause:
                # Draw a triangle representing 'play'.
                dc.DrawPolygon([(ox - 20, oy - 30),
                                (ox - 20, oy + 30),
                                (ox + 20, oy)])
            else:
                # Draw two rectangles representing 'pause'.
                dc.DrawRectangle(ox - 20, oy - 30, 15, 60)
                dc.DrawRectangle(ox + 10, oy - 30, 15, 60)

    # wx event
    def OnTimer(self, event):
        self.lock.acquire()

        if self.latest_frame is None:
            self.lock.release()
            return

        self.lock.release()

        if not self.refresh_at_next:
            return

        if self._amarec16x10_warning is not None:
            label = self.label_amarec16x10_warning
            { True: label.Show, False: label.Hide }[self._amarec16x10_warning]()
            self._amarec16x10_warning = None

        self.draw_preview()
        self.refresh_at_next = False

    def __init__(self, *args, **kwargs):
        self._prev_bmp = None
        self._enter = False
        self._pause = False

        self.refresh_at_next = False
        self.latest_frame = None
        self.lock = threading.Lock()

        wx.Panel.__init__(self, *args, **kwargs)
        self.timer = wx.Timer(self)
        self.timer.Start(100)
        self.Bind(wx.EVT_TIMER, self.OnTimer, self.timer)

        self.GetTopLevelParent().Bind(EVT_INPUT_INITIALIZED,
                                      self.on_input_initialized)
        self.GetTopLevelParent().Bind(EVT_IKALOG_PAUSE, self.on_ikalog_pause)


        # Preview
        self.preview_size = (640, 360)
        # Preview image.
        self.preview_panel = wx.Panel(self, wx.ID_ANY, size=self.preview_size)
        self.preview_panel.Bind(wx.EVT_LEFT_UP, self.on_preview_click)
        self.preview_panel.Bind(wx.EVT_ENTER_WINDOW, self.on_enter_preview)
        self.preview_panel.Bind(wx.EVT_LEAVE_WINDOW, self.on_leave_preview)

        # Video Input
        self.video_input_title_text = wx.StaticText(
            self, wx.ID_ANY, _('Video Input'))
        self.video_input_source_text = wx.StaticText(self, wx.ID_ANY, '')

        self.input_file_panel = InputFilePanel(self, wx.ID_ANY)
        self.input_file_panel.Bind(EVT_INPUT_FILE_ADDED,
                                   self.on_input_file_added)

        self.show_input_file(False)

        self.video_input_source_sizer = wx.BoxSizer(wx.HORIZONTAL)
        self.video_input_source_sizer.Add(
            self.video_input_source_text, flag=wx.LEFT, border=10)
        self.video_input_source_sizer.Add(self.input_file_panel, proportion=1)

        # Sizer to set the width of the text box to 640.
        self.video_input_sizer = wx.BoxSizer(wx.VERTICAL)
        self.video_input_sizer.Add(self.video_input_title_text)
        self.video_input_sizer.Add(self.video_input_source_sizer,
                                   flag=wx.EXPAND | wx.ALL, border=5)
        self.video_input_sizer.Add((640, 5))

        # Top sizer
        self.top_sizer = wx.BoxSizer(wx.VERTICAL)
        self.top_sizer.Add(self.video_input_sizer, flag=wx.ALL, border=5)
        self.top_sizer.Add(self.preview_panel)
        self.SetSizer(self.top_sizer)

        # AmaRec 16x10 warning should always on top layer
        self.label_amarec16x10_warning = wx.StaticText(
            self, wx.ID_ANY, _('The image seems to be 16x10. Perhaps the source is misconfigured.'), pos=(0, 0))
        self.label_amarec16x10_warning.Hide();
        self._amarec16x10_warning = None

if __name__ == "__main__":
    import sys
    import wx

    application = wx.App()
    frame = wx.Frame(None, wx.ID_ANY, 'Preview', size=(640, 360))
    preview = PreviewPanel(frame, size=(640, 360))
    layout = wx.BoxSizer(wx.VERTICAL)
    layout.Add(preview)
    frame.SetSizer(layout)
    frame.Show()
    application.MainLoop()
