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

from __future__ import print_function

import copy
import cv2
import pprint
import sys
import time
import traceback

from ikalog.utils import *
from .scenes.v2 import initialize_scenes

# The IkaLog core engine.
#


class IkaEngine:

    # Profiling

    def _profile_dump_scenes(self):
        for scene in self.scenes:
            print('%4.3fs %s' % (scene._prof_time_took, scene))

    def _profile_dump(self):
        self._profile_dump_scenes()

    def enable_profile(self):
        self._enable_profile = True

    def disble_profile(self):
        self._enable_profile = False

    # Exception Logging

    def _exception_log_init(self, context):
        context['engine']['exceptions_log'] = {}

    def _exception_log_dump(self, context):
        if not 'exceptions_log' in context['engine']:
            self._exception_log_init(context)

        if len(context['engine']['exceptions_log']) > 0:
            pprint.pprint(context['engine']['exceptions_log'])

    def _exception_log_append(self, context, name, text):
        if not 'exceptions_log' in context['engine']:
            self._exception_log_init(context)

        d = context['engine']['exceptions_log']

        count = d.get(name, {'count': 0})['count']
        d[name] = {
            'count': count + 1,
            'text': text,
        }

    # services

    def set_service(self, service_identifier, obj):
        """
        Register a service.
        Plugins can publish functions (or objects) to other plugins, as a service.
        """
        assert not service_identifier in self._services
        self._services[service_identifier] = obj

    def get_service(self, service_identifier, default=None):
        """
        Lookup and return the service registered.
        return None (or caller-specified value) if the identifier is not registered.
        """
        return self._services.get(service_identifier, default)

    # game event handlers

    def on_game_individual_result(self, context):
        self.session_close_wdt = context['engine']['msec'] + (20 * 1000)

    def on_result_gears(self, context):
        if self.session_close_wdt is not None:
            self.session_close_wdt = context['engine']['msec'] + (1 * 1000)

    def on_game_lost_sync(self, context):
        self.session_abort()

    def dprint(self, text):
        print(text, file=sys.stderr)

    def call_plugin(self, plugin, event_name,
                    params=None, debug=False, context=None):
        if not context:
            context = self.context

        if hasattr(plugin, event_name):
            if debug:
                self.dprint('Call  %s' % plugin.__class__.__name__)
            try:
                if params is None:
                    getattr(plugin, event_name)(context)
                else:
                    getattr(plugin, event_name)(context, params)
            except:
                self.dprint('%s.%s() raised a exception >>>>' %
                            (plugin.__class__.__name__, event_name))
                self.dprint(traceback.format_exc())
                self.dprint('<<<<<')

        elif hasattr(plugin, 'on_uncaught_event'):
            if debug:
                self.dprint(
                    'call plug-in hook (on_uncaught_event, %s):' % event_name)
            try:
                getattr(plugin, 'on_uncaught_event')(event_name, context)
            except:
                self.dprint('%s.%s() raised a exception >>>>' %
                            (plugin.__class__.__name__, event_name))
                self.dprint(traceback.format_exc())
                self.dprint('<<<<<')

    def call_plugins(self, event_name, params=None, debug=False, context=None):
        if not context:
            context = self.context

        if debug:
            self.dprint('call plug-in hook (%s):' % event_name)

        for op in self.output_plugins:
            self.call_plugin(op, event_name, params, debug, context)

    def call_plugins_later(self, event_name, params=None, debug=False, context=None):
        self._event_queue.append((event_name, params, context))

    def read_next_frame(self, skip_frames=0):
        context = self.context

        for i in range(skip_frames):
            frame = self.capture.read_frame()
        frame = self.capture.read_frame()

        while frame is None:
            self.call_plugins('on_frame_read_failed')
            if self._stop:
                return None, None
            cv2.waitKey(1000)
            frame = self.capture.read_frame()

        t = self.capture.get_current_timestamp()
        context['engine']['msec'] = t
        context['engine']['frame'] = frame
        context['engine']['preview'] = copy.deepcopy(frame)
        context['game']['offset_msec'] = IkaUtils.get_game_offset_msec(context)

        self.call_plugins('on_debug_read_next_frame')

        return frame, t

    def stop(self):
        if not self._stop:
            self.call_plugins('on_stop')
        self._stop = True

    def is_stopped(self):
        return self._stop

    def is_paused(self):
        return self._pause

    def reset(self):
        index = 0
        if 'game' in self.context:
            index = self.context['game'].get('index', 0)
            # Increment the value only when end_time is available,
            # (e.g. the game was finished).
            if self.context['game'].get('end_time'):
                index += 1

        # Initalize the context
        self.context['game'] = {
            # Index of this game.
            'index': index,

            'map': None,
            'rule': None,
            'won': None,
            'players': None,

            'kills': 0,
            'dead': False,
            'death_reasons': {},

            'inkling_state': [None, None],

            # Dict mapping from event_name (e.g. objective) to lists of lists
            # of msec time and value.
            # e.g. 'events': {'objective': [[0, 0], [320, 99]]}
            'events': {},

            # Float values of start and end times scince the epoch in second.
            # They are used with IkaUtils.GetTime.
            'start_time': None,
            'end_time': None,
            # Int values of start and end offset times in millisecond.
            # They are used with context['engine']['msec']
            'start_offset_msec': None,
            'end_offset_msec': None,
            # Time from start_offset_msec in msec.
            'offset_msec': None,
        }
        self.call_plugins('on_game_reset')
        self._exception_log_init(self.context)

    def create_context(self):
        prev_context = self.context
        self.context = {
            'engine': {
                'engine': self,
                'epoch_time': None,
                'source_file': None,  # file path if input is a file.
                'frame': None,
                'msec': None,
                'service': {
                    'call_plugins': self.call_plugins,
                    'call_plugins_later': self.call_plugins_later,
                    # For backward compatibility
                    'callPlugins': self.call_plugins,
                },
                'exceptions_log': {
                },
            },
            'scenes': {
            },
            # config should be nonvolatite.
            'config': prev_context.get('config', {}),
            'lobby': {
            }
        }
        self.reset()
        self.session_close_wdt = None

    def session_close(self):
        context = self.context
        self.session_close_wdt = None

        if not context['game']['end_time']:
            # end_time should be initialized in GameFinish.
            # This is a fallback in case GameFinish was skipped.
            context['game']['end_time'] = IkaUtils.getTime(context)
            context['game']['end_offset_msec'] = context['engine']['msec']

        self.call_plugins('on_game_session_end')
        self.reset()

    def session_abort(self):
        context = self.context
        self.session_close_wdt = None

        if not self.context['game']['end_time']:
            # end_time should be initialized in GameFinish or session_close.
            # This is a fallback in case they were skipped.
            context['game']['end_time'] = IkaUtils.getTime(context)
            context['game']['end_offset_msec'] = context['engine']['msec']

        self.call_plugins('on_game_session_abort')
        self.reset()

    def process_scene(self, scene):
        context = self.context

        # If input, don't run the scene
        if context['engine'].get('frame') is None:
            return False

        try:
            scene.new_frame(context)
            scene.match(context)
        except:
            if self._abort_at_scene_exception:
                raise

            scene_name = scene.__class__.__name__
            desc = traceback.format_exc()

            self.dprint('%s raised a exception >>>>' % scene_name)
            self.dprint(desc)
            self.dprint('<<<<<')

            self._exception_log_append(context, scene_name, desc)

    def find_scene_object(self, scene_class_name):
        for scene in self.scenes:
            if scene.__class__.__name__ == scene_class_name:
                return scene
        return None

    def process_frame(self):
        context = self.context

        frame, t = self.read_next_frame()

        if frame is None:
            return False

        context['engine']['inGame'] = \
            self.find_scene_object('GameTimerIcon').match(context)

        self.call_plugins('on_frame_read')

        for scene in self.scenes:
            self.process_scene(scene)

        if self.session_close_wdt is not None:
            if self.session_close_wdt < context['engine']['msec']:
                self.dprint('Watchdog fired. Closing current session')
                self.session_close()

        key = None

        self.call_plugins('on_draw_preview')
        self.call_plugins('on_show_preview')

        # FixMe: Since on_frame_next and on_key_press has non-standard arguments,
        # self.call_plugins() doesn't work for those.

        for op in self.output_plugins:
            if hasattr(op, 'on_frame_next'):
                try:
                    key = op.on_frame_next(context)
                except:
                    pass

        for op in self.output_plugins:
            if hasattr(op, 'on_key_press'):
                try:
                    op.on_key_press(context, key)
                except:
                    pass

        while len(self._event_queue) > 0:
            event = self._event_queue.pop(0)
            self.call_plugins(event_name=event[0], params=event[1], context=event[2])

    def put_source_file(self, file_path):
        return self.capture.put_source_file(file_path)

    def _main_loop(self):
        need_reset_capture = False
        while not self._stop:
            if self._pause:
                time.sleep(0.5)
                continue

            if not self.capture.is_active():
                need_reset_capture = True
                if self._keep_alive:
                    time.sleep(0.5)
                else:
                    self.stop()
                continue

            if need_reset_capture:
                self.reset_capture()
                need_reset_capture = False

            try:
                self.process_frame()
            except EOFError:
                # EOF. Close session if close_session_at_eof is set.
                if self.close_session_at_eof:
                    if self.session_close_wdt is not None:
                        self.dprint('Closing current session at EOF')
                        self.session_close()
                    else:
                        self.session_abort()

                if self.capture.on_eof():
                    self.reset_capture()
                elif self._keep_alive:
                    continue
                else:
                    self.stop()

    def run(self):
        try:
            self._main_loop()
        finally:
            if self._enable_profile:
                self._profile_dump()

            if 1:
                self._exception_log_dump(self.context)

        self.stop()

    def set_capture(self, capture):
        self.capture = capture
        self.reset_capture()

    def reset_capture(self):
        self.create_context()
        self.context['engine']['input_class'] = self.capture.__class__.__name__
        self.context['engine']['epoch_time'] = self.capture.get_epoch_time()
        self.context['engine']['source_file'] = self.capture.get_source_file()

        for scene in self.scenes:
            scene.reset()

        self.call_plugins('on_reset_capture')

    def set_plugins(self, plugins):
        self.output_plugins = [self]
        self.output_plugins.extend(self.scenes)
        self.output_plugins.extend(plugins)
        self.call_plugins('on_initialize_plugin')

    def enable_plugin(self, plugin):
        if not (plugin in self.output_plugins):
            self.dprint('%s: cannot enable plugin %s' % (self, plugin))
            return False

        self.call_plugin(plugin, 'on_enable')

    def pause(self, pause):
        self._pause = pause

    def _initialize_scenes(self):
        self.scenes = initialize_scenes(self)

    def __del__(self):
        self.call_plugins('on_engine_destroy')

    def __init__(self, enable_profile=False, abort_at_scene_exception=False,
                 keep_alive=False):
        self._initialize_scenes()

        self.output_plugins = [self]
        self._services = {}
        self.last_capture = time.time() - 100

        self._stop = False
        self._pause = True
        self._event_queue = []

        self.close_session_at_eof = False
        self._enable_profile = enable_profile
        self._abort_at_scene_exception = abort_at_scene_exception
        # Whether exit on EOFError with no next inputs.
        self._keep_alive = keep_alive

        self.context = {}
        self.create_context()
