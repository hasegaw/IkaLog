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

import json
import time
import os
import re
import subprocess
import traceback
import threading

from ikalog.plugin import IkaLogPlugin
from ikalog.utils import *


_ = Localization.gettext_translation('video_recorder', fallback=True).gettext


class Splatnet2statinkPlugin(IkaLogPlugin):

    plugin_name = 'SplatNet2statink'

    def __init__(self, dest_dir=None):
        super(Splatnet2statinkPlugin, self).__init__()

    def on_validate_configuration(self, config):
        assert config['s2s_dir'] is not None
        #assert os.path.exists(config['script_name'])
        #assert config['auto_rename'] in [True, False]
        assert config['enabled'] in [True, False]
        return True

    def on_reset_configuration(self):
        self.config['enabled'] = False
        self.config['s2s_dir'] = os.path.join('.', '')  # "./" or ".\"

    def on_set_configuration(self, config):
        self.config['enabled'] = config['enabled']
        self.config['s2s_dir'] = config['s2s_dir']

    def run_external_script(self):
        cmd = 'python3 splatnet2statink.py -c -n 1'
        print('Running %s' % cmd)

        s2s = subprocess.run(["python3", "splatnet2statink.py", "-c", "-n", "1"], stdout=subprocess.PIPE)
        s2s_stdout = s2s.stdout.decode('ascii', errors='ignore')

        return s2s_stdout


    def query_last_json(self):
        s2s_stdout = self.run_external_script()

        # trim JSON
        s2s_stdout = re.sub(r'^.[^{]+', '', s2s_stdout)

        s2s_json = json.loads(s2s_stdout)
        return s2s_json

    def worker(self, context):
        t1 = time.time()
        try:
            splatnet_json = self.query_last_json()

            t2 = time.time()

            context['game']['splatnet_json'] = splatnet_json
            IkaUtils.dprint('%s: Downloaded JSON from SplatNet2. (%s seconds)' % (self, t2-t1))
        except:
            IkaUtils.dprint('%s: Failed to download JSON from SplatNet2.' % self)
            IkaUtils.dprint(traceback.format_exc())


    def on_game_kill(self, context):
        print('aaaaaa')
    def on_game_dead(self, context):
        print('aaaaaa')

    def on_game_individual_result(self, context):
        thread = threading.Thread(target=self.worker, args=(context,))
        thread.start()


class LegacySplatnet2statink(Splatnet2statinkPlugin):

    def __init__(self, control_obs=None, dir=None):
        super(Splatnet2statink, self).__init__()

        conf = {
            'enabled':  True,
            's2s_dir': 'a',
        }

        if conf['enabled']:
            self.set_configuration(conf)


Splatnet2statink = LegacySplatnet2statink

if __name__ == '__main__':
    obj = Splatnet2statinkPlugin()
    obj.config['enabled'] = True
#    obj.query_last_json() 

    ctx = {'game': {}}
    obj.on_game_individual_result(ctx)
    time.sleep(3)
    import pprint
    pprint.pprint(ctx['game']['splatnet_json'])
