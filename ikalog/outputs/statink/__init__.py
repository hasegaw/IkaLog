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
import time
import traceback
import webbrowser

import umsgpack

from datetime import datetime
from ikalog.outputs.statink.collector import StatInkCollector
from ikalog.outputs.statink.compositor import StatInkCompositor
from ikalog.utils.statink_uploader import UploadToStatInk
from ikalog.utils import *

_ = Localization.gettext_translation('statink', fallback=True).gettext


class StatInkPlugin(StatInkCollector):

    def on_reset_configuration(self):
        config = self.config
        config['enabled'] = False
        config['api_key'] = ''
        config['endpoint_url'] = 'https://stat.ink',
        config['dry_run'] = False
        config['debug_write_payload_to_file'] = False
        config['show_response'] = False
        config['track_inklings'] = True
        config['track_special_gauge'] = True
        config['track_special_weapon'] = True
        config['track_objective'] = True
        config['track_splatzone'] = True
        config['anon_all'] = False
        config['anon_others'] = False

    def on_validate_configuration(self, config):
        boolean_params = ['enabled', 'write_payload_to_file', 'show_response', 'track_inklings',
                          'track_special_gauge', 'track_special_weapon', 'track_objective', 'track_splatzone']
        for param in boolean_params:
            assert config.get(param) in [True, False, None]

        if config['enabled']:
            assert (not config.get('api_key') in [None, ''])
        return True

    def on_set_configuration(self, new_config):
        config = self.config
        for k in new_config:
            config[k] = new_config[k]

    def close_game_session_handler(self, context):
        """
        Callback from StatInkLogger
        """

        if not (self.config['enabled'] or self.config['dry_run']):
            # This plugin is not active.
            return False

        cond = \
            (context['game'].get('map', None) != None) or \
            (context['game'].get('rule', None) != None) or \
            (context['game'].get('won', None) != None)

        if not cond:
            return False

        composer = StatInkComposer(self)
        payload = composer.compose_payload(context)

        if context['game'].get('splatnet_json', {}).get('uuid', None):
            t1 = context['game']['splatnet_json'].get('start_at')
            time_diff = abs(time.time() - t1)
            IkaUtils.dprint('%s: time diff %s' % (self, time_diff))
            if time_diff > 360:
                IkaUtils.dprint('%s: Discarding splatnet2statink data' % self)
                context['game']['splatnet_json'] = {}

        if context['game'].get('splatnet_json', {}).get('uuid', None):
            # splatnet2statink data is available - merge the results.

            ikalog_payload = payload
            payload = context['game']['splatnet_json']

            for key in ['events', 'agent', 'agent_version', 'image_result']: #ikalog_payload.keys():
                if 1: #not (key in payload):
                    payload[key] = ikalog_payload[key]
                    IkaUtils.dprint('%s: key %s merged into splatnet2statink payload: %s' % (self, key, ''))

        cond_write_payload = \
            self.config['debug_write_payload_to_file'] or self.payload_file

        if cond_write_payload:
            payload_file = IkaUtils.get_file_name(self.payload_file, context)
            self.write_payload_to_file(payload, filename=payload_file)

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
        url_statink_v2_battle = '%s/api/v2/battle' % self.config[
            'endpoint_url']

        # This function runs on worker thread.
        error, statink_response = UploadToStatInk(payload,
                                                  api_key,
                                                  url_statink_v2_battle,
                                                  self.config['show_response'],
                                                  (self.config['dry_run'] == 'server'))

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
        if self.config['dry_run'] == True:
            IkaUtils.dprint(
                '%s: Dry-run mode, skipping POST to stat.ink.' % self)
            return

        if self.payload_file:
            IkaUtils.dprint(
                '%s: payload_file is specified to %s, '
                'skipping POST to stat.ink.' % (self, self.payload_file))
            return

        if api_key is None:
            api_key = self.config['api_key']

        if api_key is None:
            raise('No API key specified')

        copied_context = IkaUtils.copy_context(context)
        call_plugins_later_func = \
            context['engine']['service']['call_plugins_later']

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

    def __init__(self):
        super(StatInkPlugin, self).__init__()


class StatInk(StatInkPlugin):
    """
    Legacy Plugin interface
    """

    def __init__(self, api_key=None, track_objective=False,
                 track_splatzone=False, track_inklings=False,
                 track_special_gauge=False, track_special_weapon=False,
                 anon_all=False, anon_others=False,
                 debug=False, dry_run=False, url='https://stat.ink',
                 video_id=None, payload_file=None):
        super(StatInk, self).__init__()

        config = self.config
        config['enabled'] = not (api_key in ['', None])
        config['api_key'] = api_key
        config['endpoint_url'] = url
        config['dry_run'] = dry_run
        config['debug_write_payload_to_file'] = False
        config['show_response'] = debug
        config['track_inklings'] = track_inklings
        config['track_special_gauge'] = track_special_gauge
        config['track_special_weapon'] = track_special_weapon
        config['track_objective'] = track_objective
        config['track_splatzone'] = track_splatzone
        config['anon_all'] = anon_all
        config['anon_others'] = anon_others

        self.video_id = video_id
        self.payload_file = payload_file
