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

import threading
import os
import time

import cv2

from ikalog.utils import IkaUtils
from ikalog.inputs.filters import OffsetFilter


class VideoInput(object):

    ##
    # cap_optimal_input_resolution
    # tells if the device feeds the image in optimal resolution
    # (720p or 1080p). if True, the input will perform strict check
    # for input resolution.
    cap_optimal_input_resolution = True

    ##
    # cap_recorded_video
    cap_recorded_video = False

    out_width = 1280
    out_height = 720

    ##
    # _initialize_driver_func()
    # Handler for source-specific initialization.
    # @param self    the object
    def _initalize_driver_func(self):
        raise

    ##
    # _initialize_driver_func()
    # Handler for source-specific cleanup.
    # @param self    the object
    def _cleanup_driver_func(self):
        raise

    ##
    # _select_device_by_index_func()
    # @param self    the object
    # @param index     the device_id to be selected.
    def _select_device_by_index_func(self, index):
        raise

    ##
    # _select_device_by_index_func()
    # @param self    the object
    # @param index     the device name to be selected.
    def _select_device_by_name_func(self, name):
        raise

    ##
    # _is_active_func()
    # @param self    the object
    # @return     True if the input is active. Otherwise False.
    def _is_active_func(self):
        raise

    ##
    # _enumerate_devices_func()
    # @param self    the object
    # @return        List of enumerated devices.
    def _enumerate_sources_func(self):
        raise

    ##
    # _next_frame_func()
    # @param self    the object
    def _next_frame_func(self):
        pass

    ##
    # _read_frame_func()
    # @param self    the object
    # @return        the current frame of the input source.
    def _read_frame_func(self):
        raise

    ##
    # is_active()
    # Returns the state of the input source.
    # @return True if the input source is active. Otherwise False.
    def is_active(self):
        return self._is_active_func()

    ##
    # enumerate_sources()
    # Returns the list of enumerated devices on the system.
    # @return The list of enumerated devices.
    def enumerate_sources(self):
        # FIXME: Cache.
        return self._enumerate_sources_func()

    ##
    # select_source(self,index=None,name=None)
    # @param  index    index(int) of device to be selected.
    # @param  name     name(int) of device to be selected.
    # @return True if the device is initialize and ready. Otherwise False.
    def select_source(self, index=None, name=None):
        by_index = (index is not None)
        by_name = (name is not None)

        assert by_index or by_name
        assert not (by_index and by_name)

        if by_index:
            r = self._select_device_by_index_func(index)
        else:
            r = self._select_device_by_name_func(name)

        self.set_frame_rate(None)  # Default framerate

    ##
    #
    def _skip_frame_realtime(self):
        current_tick = self.get_tick()
        last_tick = self.last_tick
        next_tick = current_tick

        if self.fps_requested is not None:
            next_tick2 = int(last_tick + (1000 / self.fps_requested * 2))
            if current_tick < next_tick2:
                next_tick = int(last_tick + (1000 / self.fps_requested))

        while current_tick < next_tick:
            time.sleep(0.05)
            current_tick = self.get_tick()

        return next_tick

    def _skip_frame_recorded(self):

        if self.frame_skip_rt:
            tick = self.get_tick()
        elif self.fps_requested is not None:
            tick = self.get_current_timestamp() + (1000 / self.fps_requested)
        else:
            return

        video_msec = self.get_current_timestamp()
        skip = video_msec < tick
        while skip:
            frame_ = self._read_frame_func()

            video_msec = self.get_current_timestamp()
            skip = video_msec < tick

        return None

    ##
    # read_frame(self)
    #
    # read a frame from the input. The device should have been
    # activated by select_device() method.
    #
    # @return Image if capture succeeded. Otherwise None.
    def read_frame(self):
        self.lock.acquire()
        if not self.is_active():
            self.lock.release()
            return None

        next_tick = None

        if self.cap_recorded_video:
            self._skip_frame_recorded()
        else:
            next_tick = self._skip_frame_realtime()

        self._next_frame_func()

        img = self._read_frame_func()
        self.lock.release()

        if img is None:
            return None

        if self.cap_optimal_input_resolution:
            res720p = (img.shape[0] == 720) and (img.shape[1] == 1280)
            res1080p = (img.shape[0] == 1080) and (img.shape[1] == 1920)

            if not (res720p or res1080p):
                IkaUtils.dprint(
                    'Invalid input resolution (%dx%d). Acceptable res: 1280x720 or 1920x1080' %
                    (img.shape[1], img.shape[0])
                )
                return None

        if next_tick is not None:
            self.last_tick = next_tick

        # need stratch?
        stratch = (
            img.shape[0] != self.output_geometry[0] or
            img.shape[1] != self.output_geometry[1])

        if stratch:
            img = cv2.resize(
                img,
                (self.output_geometry[1], self.output_geometry[0]),
                # fixme
            )

        img = self._offset_filter.execute(img)
        return img

    def _get_current_timestamp_func(self):
        return self.get_tick()
    ##
    # reset(self)
    #
    # Reset the source plugin. It still try to keep current device active.

    def reset_tick(self):
        self._base_tick = int(time.time() * 1000)
        self.last_tick = 0

    def get_tick(self):
        return int(time.time() * 1000 - self._base_tick)

    def reset(self):
        pass

    ##
    # get_current_timestamp(self)
    #
    # Get current timestamp information.
    # @return Timestamp (in msec)
    def get_current_timestamp(self):
        return self._get_current_timestamp_func()

    def get_epoch_time(self):
        return None

    def set_pos_msec(self, pos_msec):
        pass

    ##
    # set_frame_rate(self, fps=None, realtime=False)
    #
    # Specify input frame rate desired.
    # If realtime mode is enabled, the plugin will drop
    # frames to perform real-time playback.
    #
    # @param fps      frames per second to be read
    # @param realtime Realtime mode if True.
    def set_frame_rate(self, fps=None, realtime=False):
        if not self.is_active():
            return

        self.fps_requested = fps
        self.frame_skip_rt = realtime

    def set_offset(self, offset=None):
        if offset is None:
            self._offset_filter.disable()

        else:
            assert len(offset) == 2
            self._offset_filter.offset = offset
            self._offset_filter.enable()

    ##
    # Backward compatibility.
    def start_camera(self, source):
        IkaUtils.dprint(
            '%s: start_camera() is deprcated. Use select_source().' % self)
        IkaUtils.dprint('   start_camera(index=1)')
        IkaUtils.dprint('   start_camera(name="my capture device")')
        raise Exception()

    ##
    # Constructor.
    #
    def __init__(self):
        self.output_geometry = (720, 1280)
        self.effective_lines = 720
        self.lock = threading.Lock()

        self.is_realtime = True
        self.reset()
        self.reset_tick()
        self._offset_filter = OffsetFilter(self)

        self.set_frame_rate()
        self._initialize_driver_func()
