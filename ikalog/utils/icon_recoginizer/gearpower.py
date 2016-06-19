#!/usr/bin/env python3
# -*- coding: utf-8 -*-
#
#  IkaLog
#  ======
#  Copyright (C) 2015 Takeshi HASEGAWA
#  Copyright (C) 2015 Hiromichi Itoh
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


from ikalog.utils.icon_recoginizer import IconRecoginizer


class GearPowerRecoginizer(IconRecoginizer):

    def model_filename(self):
        return 'data/gearpowers.knn.data'

    def load_model_from_file(self, model_file=None):
        if model_file is None:
            model_file = self.model_filename()

        super(GearPowerRecoginizer, self).load_model_from_file(model_file)

    def save_model_to_file(self, model_file=None):
        if model_file is None:
            model_file = self.model_filename()

        super(GearPowerRecoginizer, self).save_model_to_file(model_file)

    def __new__(cls, *args, **kwargs):

        if not hasattr(cls, '__instance__'):
            cls.__instance__ = super(
                GearPowerRecoginizer, cls).__new__(cls, *args, **kwargs)

        return cls.__instance__

    def __init__(self, model_file=None):

        if hasattr(self, 'trained') and self.trained:
            return

        super(GearPowerRecoginizer, self).__init__()
