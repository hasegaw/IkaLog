
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

import cv2
import numpy as np
from PIL import Image


def imread(filename):
    if not os.path.exists(filename):
        return None

    f = open(filename, 'rb')
    img_bytes = f.read()
    f.close()

    img = cv2.imdecode(np.fromstring(img_bytes, dtype='uint8'), 1)
    return img
