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

import gettext
import os
import re


class Localization(object):

    _game_language = None
    _language = None

    @staticmethod
    def get_languages_from_envvars():
        languages = []
        for env_key in ('LANGUAGE', 'LC_ALL', 'LC_MESSAGES', 'LANG'):
            lang = os.environ.get(env_key)
            if lang:
                return lang
                # return Localization.expand_languages(lang)
        return None

    @staticmethod
    def expand_languages(languages):
        if isinstance(languages, list):
            return languages

        assert isinstance(languages, str)

        langs = []
        for lang in languages.split(':'):
            langs.append(lang)

        for lang in langs:
            lang_short = re.sub('_.*', '', lang)
            if not lang_short in langs:
                langs.append(lang_short)

        return langs

    @staticmethod
    def set_game_languages(lang):
        Localization._game_language = lang
        pass

    @staticmethod
    def get_game_languages():
        lang = Localization._game_language
        if lang is not None:
            return Localization.expand_languages(lang)

        lang = os.environ.get('IKALOG_LANG', 'ja')
        return Localization.expand_languages(lang)

    @staticmethod
    def set_languages(lang):
        Localization._language = lang
        pass

    @staticmethod
    def get_languages():
        lang = Localization._language
        if lang is not None:
            return Localization.expand_languages(lang)

        lang = Localization.get_languages_from_envvars()
        if lang is not None:
            return Localization.expand_languages(lang)

        lang = os.environ.get('IKALOG_LANG', 'ja')
        return Localization.expand_languages(lang)

    @staticmethod
    def gettext_translation(domain, localdir=None, languages=None, class_=None, fallback=False, codeset=None):
        if languages is None:
            languages = Localization.get_languages()

        if localdir is None:
            localdir = os.path.join(
                # IkaUtils.baseDirectory(),
                'locale'
            )

        return gettext.translation(domain, localdir, fallback=True)

    @staticmethod
    def print_language_settings():
        from ikalog.utils import IkaUtils
        IkaUtils.dprint('IkaLog Primary CLI Language: %s (set LANG to override)'
                        % Localization.get_languages()[0])
        IkaUtils.dprint('IkaLog Game Language: %s (set IKALOG_LANG to override)'
                        % Localization.get_game_languages()[0])
