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

# Usage:
#   $ export CS=xxxx
#   $ export CK=xxxx
#   $ export AT=xxxx
#   $ export ATS=xxxx
#   $ wget http://...../sheryl.jpg
#   $ py.test-3.4 test/outputs/test_twitter.py

import os
import time
import unittest

import cv2

class TestTwitter(unittest.TestCase):

    def _load_twitter_plugin(self):
        from ikalog.outputs import Twitter
        twitter = Twitter(
            os.environ['CS'],
            os.environ['CK'],
            os.environ['AT'],
            os.environ['ATS'],
        )

        return twitter

    def _load_sample_media(self):
        img = cv2.imread('sheryl.jpg')
        assert img is not None
        return img
    
    #
    # Test Cases
    #

    def test_tweet(self):
        twitter = self._load_twitter_plugin()
        img = self._load_sample_media()
        media_id = twitter.post_media(img)
        print('media_id is ', media_id)
        response = twitter.tweet('@hasegaw_bot シェリル %d' % int(time.time()), media=media_id)
        assert response.status_code == 200
