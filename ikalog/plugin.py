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


class IkaLogPlugin(object):

    def get_configuration(self):
        if hasattr(self, 'on_get_configuration'):
            return self.on_get_configuration()
        return self.config.copy()

    def validate_configuration(self, config):
        if hasattr(self, 'on_validate_configuration'):
            return self.on_validate_configuration(config)
        return True

    def set_configuration(self, config):
        self.validate_configuration(config)
        self.on_set_configuration(config)

    def __init__(self):
        self.config = {}
        self.on_reset_configuration()
