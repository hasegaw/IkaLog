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

import gettext
import os
import sys
import time
import traceback

import wx

from ikalog.utils import IkaUtils, Localization

Localization.print_language_settings()

# from ikalog.engine import *
from ikalog import outputs
from ikalog.engine import *
from ikalog.ui.panel import *
from ikalog.ui import VideoCapture, IkaLogGUI

_ = Localization.gettext_translation('IkaUI', fallback=True).gettext


def IkaUI_main():
    IkaUtils.dprint(_('Hello!'))

    application = wx.App()
    input_plugin = VideoCapture()

    engine = IkaEngine(keep_alive=True)
    engine.close_session_at_eof = True
    engine.set_capture(input_plugin)

    # 設定画面を持つ各種 Output Plugin
    # -> 設定画面の生成とプラグインリストへの登録
    outputs_with_gui = [
        outputs.CSV(),
        # outputs.Fluentd(),
        outputs.JSON(),
        # outputs.Hue(),
        outputs.OBS(),
        outputs.Twitter(),
        outputs.Screenshot(),
        outputs.Boyomi(),
        outputs.Slack(),
        outputs.StatInk(),
        outputs.DebugVideoWriter(),
        outputs.WebSocketServer(),
    ]
    gui = IkaLogGUI(engine, outputs_with_gui)

    plugins = []

    # とりあえずデバッグ用にコンソールプラグイン
    plugins.append(outputs.Console())

    # 各パネルをプラグインしてイベントを受信する
    plugins.append(gui.preview)
    plugins.append(gui.last_result)

    # 設定画面を持つ input plugin もイベントを受信する
    plugins.append(input_plugin)

    # UI 自体もイベントを受信
    plugins.append(gui)

    plugins.extend(outputs_with_gui)

    # 本当に困ったときのデバッグログ増加モード
    if 'IKALOG_DEBUG' in os.environ:
        plugins.append(outputs.DebugLog())

    # プラグインリストを登録
    engine.set_plugins(plugins)

    gui.run()
    application.MainLoop()

    IkaUtils.dprint(_('Bye!'))

if __name__ == '__main__':
    try:
        IkaUI_main()
    except:
        IkaUtils.dprint('\n\nIkaUI got an exception and crashed >>>>')
        IkaUtils.dprint(traceback.format_exc())
        IkaUtils.dprint('<<<<')

        if hasattr(sys, 'frozen'):
            while(True):
                time.sleep(1)
