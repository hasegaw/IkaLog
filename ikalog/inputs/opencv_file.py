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
import threading

import cv2
from ikalog.utils import *
from ikalog.inputs import VideoInput


class CVFile(VideoInput):

    cap_recorded_video = True

    # override
    def _initialize_driver_func(self):
        # OpenCV File doesn't need pre-initialization.
        self._cleanup_driver_func()

    # override
    def _cleanup_driver_func(self):
        self.lock.acquire()
        try:
            if self.video_capture is not None:
                self.video_capture.release()
            self.reset()
        finally:
            self.lock.release()

    # override
    def _is_active_func(self):
        return (self.video_capture is not None)

    # override
    def _select_device_by_index_func(self, source):
        raise Exception(
            '%s does not support selecting device by index.' % self)

    # override
    def _select_device_by_name_func(self, source):
        self.lock.acquire()
        try:
            if self.is_active():
                self.video_capture.release()

            self.reset()
            # FIXME: Does it work with non-ascii path?
            self.video_capture = cv2.VideoCapture(source)
            self._source_file = source
            if self.video_capture.isOpened():
                self._epoch_time = self.get_start_time()
            else:
                self.video_capture = None
            self.reset_tick()

        finally:
            self.lock.release()

        return self.is_active()

    # override
    def _next_frame_func(self):
        pass

    # override
    def _get_current_timestamp_func(self):
        video_msec = self.video_capture.get(cv2.CAP_PROP_POS_MSEC)

        if video_msec is None:
            return self.get_tick()

        return video_msec

    # override
    def _read_frame_func(self):
        ret, frame = self.video_capture.read()
        if not ret:
            raise EOFError()

        if self.frame_skip_rt:
            systime_msec = self.get_tick()
            video_msec = self.video_capture.get(cv2.CAP_PROP_POS_MSEC)
            assert systime_msec >= 0

            skip = video_msec < systime_msec
            while skip:
                ret, frame_ = self.video_capture.read()

                if not ret:
                    break

                frame = frame_
                video_msec = self.video_capture.get(cv2.CAP_PROP_POS_MSEC)
                skip = video_msec < systime_msec

        return frame

    # override
    def get_epoch_time(self):
        if self._use_file_timestamp:
           return self._epoch_time
        else:
            return None

    def get_start_time(self):
        """Returns the timestamp of the beginning of this video in sec."""
        if (not self._source_file) or (not self.video_capture):
            return None

        last_modified_time = os.stat(self._source_file).st_mtime

        frames = self.video_capture.get(cv2.CAP_PROP_FRAME_COUNT)
        fps = self.video_capture.get(cv2.CAP_PROP_FPS)
        duration = frames / fps

        return last_modified_time - duration

    # override
    def set_pos_msec(self, pos_msec):
        """Moves the video position to |pos_msec| in msec."""
        self.video_capture.set(cv2.CAP_PROP_POS_MSEC, pos_msec)

    # override
    def get_source_file(self):
        return self._source_file

    def set_use_file_timestamp(self, use_file_timestamp=True):
        self._use_file_timestamp = use_file_timestamp

    def __init__(self):
        self.video_capture = None
        self._source_file = None
        self._epoch_time = None
        self._use_file_timestamp = True
        super(CVFile, self).__init__()

    # backward compatibility
    def start_video_file(self, source):
        IkaUtils.dprint(
            '%s: start_video_file() is deprcated. Use select_source(name="filename.mp4")' % self)
        self.select_source(name=source)

if __name__ == "__main__":
    import sys

    f = sys.argv[1]

    obj = CVFile()
    obj.select_source(name=f)
    obj.set_frame_rate(realtime=True)

    k = 0
    while k != 27:
        frame = obj.read_frame()
        if frame is not None:
            cv2.imshow(obj.__class__.__name__, frame)
        cv2.waitKey(1)
