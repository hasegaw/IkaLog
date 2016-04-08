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
import sys

sys.path.append('.')
base_dir = sys.argv[1]

from ikalog.utils import WeaponRecoginizer

weapons = WeaponRecoginizer()
weapons.load_model_from_file()
weapons.knn_train()

weapons.test_samples_from_directory(base_dir)
weapons.dump_test_results_html(short=True)
