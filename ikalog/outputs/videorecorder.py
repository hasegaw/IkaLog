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

import time
import os
import traceback
import threading

from ikalog.plugin import IkaLogPlugin
from ikalog.utils import *


_ = Localization.gettext_translation('video_recorder', fallback=True).gettext


def create_mp4_filename(context):
    # FIXME: i18n

    map = IkaUtils.map2text(context['game']['map'], unknown='マップ不明')
    rule = IkaUtils.rule2text(context['game']['rule'], unknown='ルール不明')
    won = IkaUtils.getWinLoseText(
        context['game']['won'], win_text='win', lose_text='lose')

    time_str = time.strftime("%Y%m%d_%H%M", time.localtime())
    newname = '%s_%s_%s_%s.mp4' % (time_str, map, rule, won)

    return newname


class VideoRecorderPlugin(IkaLogPlugin):

    plugin_name = 'VideoRecorder'

    def __init__(self, dest_dir=None):
        super(VideoRecorderPlugin, self).__init__()

    def on_validate_configuration(self, config):
        assert config['dest_dir'] is not None
        # assert os.path.exists(config['dest_dir'])
        assert os.path.exists(config['script_name'])
        assert config['auto_rename'] in [True, False]
        assert config['enabled'] in [True, False]
        return True

    def on_reset_configuration(self):
        # self.config['dest_dir'] = 'screeenshots/'

        self.config['enabled'] = False
        self.config['auto_rename'] = False
        self.config['script_name'] = False

    def on_set_configuration(self, config):
        self.config['enabled'] = config['enabled']
        self.config['auto_rename'] = config['auto_rename']
        self.config['script_name'] = config['script_name']

    def run_external_script(self, mode):
        cmd = '%s %s' % (self.control_obs, mode)
        print('Running %s' % cmd)
        try:
            os.system(cmd)
        except:
            print(traceback.format_exc())

    """
    aaa
    """

    def run_test(self):
        """
        Run the specficified script in test mode.
        """
        self.run_external_script('test')

    def run_start(self):
        self.run_external_script('start')

    def run_stop(self):
        self.run_external_script('stop')

    """
    Event handlers
    """

    def on_lobby_matched(self, context):
        if not self.config['enabled']:
            return False

        self.run_start()

    def set_basic_variables(self, context):
        # Set Environment variables.
        game = context['game']
        map = game.get('map', 'unknown')
        rule = game.get('rule', 'unknown')
        won = IkaUtils.getWinLoseText(
            game['won'], win_text='win', lose_text='lose', unknown_text='unknown')

        # Environment variables setup

        os.environ['IKALOG_STAGE'] = map
        os.environ['IKALOG_RULE'] = rule
        os.environ['IKALOG_WON'] = won
        #os.environ['IKALOG_TIMESTAMP'] = time.strftime("%Y%m%d_%H%M", context['game']['timestamp'])

    def on_game_individual_result(self, context):
        if not self.config['enabled']:
            return False

        self.set_basic_variables(context)

        # Environment variables setup for auto-renaming

        if self.config['auto_rename']:
            os.environ['IKALOG_MP4_DESTNAME'] = \
                os.path.join(self.config['dest_dir'],
                             create_mp4_filename(context))
            os.environ['IKALOG_MP4_DESTDIR'] = \
                os.path.join(self.config['dest_dir'], '')

        # Since we want to stop recording asyncnously,
        # This function is called by independent thread.
        # Note the context can be unexpected value.

        thread = threading.Thread(target=self.run_stop)
        thread.start()


class LegacyOBS(VideoRecorderPlugin):

    def __init__(self, control_obs=None, dir=None):
        super(LegacyOBS, self).__init__()

        conf = {
            'enabled':  (not control_obs is None),
            'auto_rename': (dir is not None),
            'dest_dir': dir,
            'script_name': control_obs,
        }

        if conf['enabled']:
            self.set_configuration(conf)

OBS = LegacyOBS
