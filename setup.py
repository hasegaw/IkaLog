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

from distutils.core import setup
import os
import py2exe

Mydata_files = []
dir = 'masks/'
for files in os.listdir(dir):
	f1 = dir + files
	if os.path.isfile(f1): # skip directories
		f2 = 'masks', [f1]
		Mydata_files.append(f2)

setup(
	console=['IkaUI.py'],
	data_files = Mydata_files,
	zipfile = None,
	options = {
		'py2exe': {
			'bundle_files': 1,
			'unbuffered': True,
			'optimize': 2,
			'compressed': 1,
		}
	
	}
)

#	'name': 'IkaLog',
#	'company_name': 'Project IkaLog',
#	'url': 'https://github.com/hasegaw/IkaLog',
#	'description': 'Enjoy Splatoon!',
#	'version': '0.01',
