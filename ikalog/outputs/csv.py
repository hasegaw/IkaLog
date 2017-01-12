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
import traceback

from ikalog.plugin import IkaLogPlugin
from ikalog.utils import *

_ = Localization.gettext_translation('csv', fallback=True).gettext


def _result_scoreboard2text(context):
    game = context.get('game', {})
    map = IkaUtils.map2text(game.get('map'))
    rule = IkaUtils.rule2text(game.get('rule'))
    won = IkaUtils.getWinLoseText(
        game.get('won'), win_text='勝ち', lose_text='負け', unknown_text='不明')

    t = IkaUtils.get_end_time(context)
    t_unix = int(time.mktime(t.timetuple()))
    t_str = t.strftime("%Y,%m,%d,%H,%M")
    s_won = IkaUtils.getWinLoseText(
        won, win_text="勝ち", lose_text="負け", unknown_text="不明")

    return "%s,%s,%s,%s,%s\n" % (t_unix, t_str, map, rule, won)


def _append_file(filename, record):
    with open(filename, 'a') as file:
        file.write(record)


class CSVPlugin(IkaLogPlugin):
    """
    Configuration read/write
    """
    plugin_name = "CSV"

    def on_validate_configuration(self, config):
        assert config['enabled'] in [True, False]
        assert config['filename'] is not None
        return True

    def on_reset_configuration(self):
        self.config['filename'] = ''
        self.config['enabled'] = False

    def on_set_configuration(self, config):
        self.config['filename'] = config['filename']
        self.config['enabled'] = config['enabled']

    def on_game_session_end(self, context):
        IkaUtils.dprint('%s (enabled = %s)' % (self, self.config['enabled']))

        if not self.config['enabled']:
            return

        record = _result_scoreboard2text(context)
        try:
            _append_file(self.config['filename'], record)
        except:  # FIXE
            IkaUtils.dprint('CSV: Failed to write CSV File')
            IkaUtils.dprint(traceback.format_exc())

    def __init__(self):
        super(CSVPlugin, self).__init__()


class LegacyCSV(CSVPlugin):

    def __init__(self, csv_filename=None):
        super(CSVPlugin, self).__init__()

        config = self.get_configuration()
        config['filename'] = csv_filename
        config['enabled'] = (csv_filename is not None)
        self.set_configuration(config)

CSV = LegacyCSV
