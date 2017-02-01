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

import json
import os
import sys
import traceback
from ikalog.utils import IkaUtils

def _get_plugins_list(engine):
    r = {}
    cond = lambda x: hasattr(x, 'get_configuration')
    plugins = filter(cond, engine.output_plugins)
    for plugin in plugins:# engine.output_plugins:
        if hasattr(plugin, 'plugin_name'):
            plugin_name = plugin.plugin_name
        else:
            plugin_name = plugin.__class__.__name__

        r[plugin_name] = plugin
    return r

def generate_config(engine):
    plugins = _get_plugins_list(engine)

    config = {}
    for plugin_name in plugins.keys():
        plugin = plugins[plugin_name]
        config[plugin_name] = plugin.get_configuration()
        if 'read_only' in config[plugin_name]:
            del config[plugin_name]['read_only']

    return config

def write_to_file(engine, filename):
    config = generate_config(engine)
    try:
        json_file = open(filename, 'w')
        json_file.write(json.dumps(config)) #, separators=(',', ':')) + '\n')
        json_file.close()
    except:
        print("JSON: Failed to write JSON file")
        IkaUtils.dprint(traceback.format_exc())


def read_from_file(engine, filename):
    try:
        f = open(filename, 'r')
        config = json.load(f)
    except FileNotFoundError as e:
        IkaUtils.dprint("No configuration file to read.")
        return False

    except:
        IkaUtils.dprint("JSON: Failed to read JSON file")
        IkaUtils.dprint(traceback.format_exc())
        return False

    plugins = _get_plugins_list(engine)
    for plugin_name in plugins.keys():
        if not (plugin_name in config):
            print('no data for %s' % plugin_name)
            continue
        print('loading for %s' % plugin_name)
        plugins[plugin_name].set_configuration(config[plugin_name])
