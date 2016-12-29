#!/usr/bin/env python3
# -*- coding: utf-8 -*-
#
#  IkaLog
#  ======
#  Copyright (C) 2016 Takeshi HASEGAWA
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
import pprint
import threading
import traceback
import webbrowser

import umsgpack

from datetime import datetime
from ikalog.outputs.statink.collector import StatInkCollector
from ikalog.outputs.statink.compositor import StatInkCompositor
from ikalog.utils.statink_uploader import UploadToStatInk
from ikalog.utils import *

_ = Localization.gettext_translation('statink', fallback=True).gettext


class StatInk(StatInkCollector):

    def close_game_session_handler(self, context):
        """
        Callback from StatInkLogger
        """

        IkaUtils.dprint('%s (enabled = %s)' % (self, self.enabled))

        if (not self.enabled) and (not self.dry_run):
            return False

        cond = \
            (context['game'].get('map', None) != None) or \
            (context['game'].get('rule', None) != None) or \
            (context['game'].get('won', None) != None)

        if not cond:
            return

        compositor = StatInkCompositor(self)
        payload = compositor.composite_payload(context)

        if self.debug_writePayloadToFile or self.payload_file:
            payload_file = IkaUtils.get_file_name(self.payload_file, context)
            self.write_payload_to_file(payload, filename=payload_file)

        # FIXME: Dry-run not supported
        self.post_payload(context, payload)

    def write_response_to_file(self, r_header, r_body, basename=None):
        if basename is None:
            t = datetime.now().strftime("%Y%m%d_%H%M")
            basename = os.path.join('/tmp', 'statink_%s' % t)

        try:
            f = open(basename + '.r_header', 'w')
            f.write(r_header)
            f.close()
        except:
            IkaUtils.dprint('%s: Failed to write file' % self)
            IkaUtils.dprint(traceback.format_exc())

        try:
            f = open(basename + '.r_body', 'w')
            f.write(r_body)
            f.close()
        except:
            IkaUtils.dprint('%s: Failed to write file' % self)
            IkaUtils.dprint(traceback.format_exc())

    def write_payload_to_file(self, payload, filename=None):
        if filename is None:
            t = datetime.now().strftime("%Y%m%d_%H%M")
            filename = os.path.join('/tmp', 'statink_%s.msgpack' % t)

        try:
            f = open(filename, 'wb')
            umsgpack.pack(payload, f)
            f.close()
        except:
            IkaUtils.dprint('%s: Failed to write msgpack file' % self)
            IkaUtils.dprint(traceback.format_exc())

    def _post_payload_worker(self, context, payload, api_key,
                             call_plugins_later_func=None):
        # This function runs on worker thread.
        error, statink_response = UploadToStatInk(payload,
                                                  api_key,
                                                  self.url_statink_v1_battle,
                                                  self.show_response_enabled,
                                                  (self.dry_run == 'server'))

        if not call_plugins_later_func:
            return

        # Trigger a event.
        if error:
            call_plugins_later_func(
                'on_output_statink_submission_error',
                params=statink_response, context=context
            )

        elif statink_response.get('id', 0) == 0:
            call_plugins_later_func(
                'on_output_statink_submission_dryrun',
                params=statink_response, context=context
            )

        else:
            call_plugins_later_func(
                'on_output_statink_submission_done',
                params=statink_response, context=context
            )

    def post_payload(self, context, payload, api_key=None):
        if self.dry_run == True:
            IkaUtils.dprint(
                '%s: Dry-run mode, skipping POST to stat.ink.' % self)
            return

        if self.payload_file:
            IkaUtils.dprint(
                '%s: payload_file is specified to %s, '
                'skipping POST to stat.ink.' % (self, self.payload_file))
            return

        if api_key is None:
            api_key = self.api_key

        if api_key is None:
            raise('No API key specified')

        copied_context = IkaUtils.copy_context(context)
        call_plugins_later_func = context['engine'][
            'service']['call_plugins_later']

        thread = threading.Thread(
            target=self._post_payload_worker,
            args=(copied_context, payload, api_key, call_plugins_later_func))
        thread.start()

    def print_payload(self, payload):
        payload = payload.copy()

        for k in ['image_result', 'image_judge', 'image_gear']:
            if k in payload:
                payload[k] = '(PNG Data)'

        if 'events' in payload:
            payload['events'] = '(Events)'

        pprint.pprint(payload)

    def __init__(self, api_key=None, track_objective=False,
                 track_splatzone=False, track_inklings=False,
                 track_special_gauge=False, track_special_weapon=False,
                 anon_all=False, anon_others=False,
                 debug=False, dry_run=False, url='https://stat.ink',
                 video_id=None, payload_file=None):
        super(StatInk, self).__init__()

        self.enabled = not (api_key is None)
        self.api_key = api_key
        self.dry_run = dry_run
        self.debug_writePayloadToFile = False
        self.show_response_enabled = debug
        self.track_inklings_enabled = track_inklings
        self.track_special_gauge_enabled = track_special_gauge
        self.track_special_weapon_enabled = track_special_weapon
        self.track_objective_enabled = track_objective
        self.track_splatzone_enabled = track_splatzone
        self.anon_all = anon_all
        self.anon_others = anon_others

        self.url_statink_v1_battle = '%s/api/v1/battle' % url

        self.video_id = video_id
        self.payload_file = payload_file
