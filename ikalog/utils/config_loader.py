#!/usr/local/bin/python3
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

import IkaConfig

from ikalog import inputs
from ikalog import outputs


def _init_source(opts):
    # 使いたい入力を設定
    source = None

    # Set the input type
    input_type = (opts.get('input') or IkaConfig.INPUT_SOURCE)
    if opts.get('input_file'):
        input_type = 'CVFile'
    if not input_type:
        input_type = 'GStreamer'

    # Set the input arguments
    input_args = (IkaConfig.INPUT_ARGS.get(input_type) or {})

    # パターン1: Windows 上でキャプチャデバイスを利用(DirectShow)
    if input_type == 'DirectShow':
        source = inputs.DirectShow()
        source.select_source(input_args.get('device'))
        return source

    # パターン2: OpenCV VideoCapture 経由でキャプチャデバイスを利用
    if input_type == 'CVCapture':
        source = inputs.CVCapture()
        source.select_source(input_args.get('device'))
        return source

    # パターン3: Windows 上でスクリーンキャプチャを利用
    # 起動時は全画面を取り込み。 C キー押下で画面内にある WiiU 画面を検出
    if input_type == 'ScreenCapture':
        source = inputs.ScreenCapture()
        return source

    # パターン4: Mac 上で AVFoundation を介してキャプチャデバイスを利用
    # 現在 UltraStudio Mini Recorder のみ動作確認
    if input_type == 'AVFoundationCapture':
        source = inputs.AVFoundationCapture()
        source.select_source(input_args.get('source'))
        return source

    # パターン5: OpenCV のビデオファイル読み込み機能を利用する
    # OpenCV が FFMPEG に対応していること
    # 直接ファイルを指定するか、コマンドラインから --input_file で指定可能
    if input_type == 'CVFile':
        source = inputs.CVFile()
        source.select_source(name=(opts.get('input_file') or
                                   input_args.get('source')))
        source.set_frame_rate(input_args.get('frame_rate'))
        return source

    # パターン6: OpenCV の GStreamerパイプラインからの読み込み機能を利用する
    # ・OpenCV が GStreamer に対応していること
    # ・パイプラインは '$YOUR_STREAM_SOURCE ! videoconvert ! appsink'
    #
    # 例) Blackmagic Design社のキャプチャデバイスのHDMIポートから720p 59.94fpsで取得する場合
    # source = inputs.GStreamer()
    # source.select_source(name='decklinksrc connection=hdmi mode=720p5994 device-number=0 ! videoconvert ! appsink')
    #
    # 例) テストパターンを表示
    if input_type == 'GStreamer':
        source = inputs.GStreamer()
        source.select_source(name=input_args.get('source'))
        return source

    return source


def _init_outputs(opts):
    # 使いたいプラグインを適宜設定
    OutputPlugins = []

    output_plugins = IkaConfig.OUTPUT_PLUGINS

    # Set output_args with command line options.
    output_args = IkaConfig.OUTPUT_ARGS.copy()

    # Screen: IkaLog 実行中にキャプチャ画像を表示します。
    if 'Screen' in output_plugins:
        OutputPlugins.append(outputs.Screen(**output_args['Screen']))

    # Console(): 各種メッセージを表示します。
    if 'Console' in output_plugins:
        OutputPlugins.append(outputs.Console(**output_args['Console']))

    # IkaOutput_CSV: CSVログファイルを出力します。
    if 'CSV' in output_plugins:
        OutputPlugins.append(outputs.CSV(**output_args['CSV']))

    # Fluentd: Fluentd にデータを投げます。
    if 'Fluentd' in output_plugins:
        OutputPlugins.append(outputs.Fluentd(**output_args['Fluentd']))

    if 'Hue' in output_plugins:
        OutputPlugins.append(outputs.Hue(**output_args['Hue']))

    # JSON: JSONログファイルを出力します。
    if 'JSON' in output_plugins:
        OutputPlugins.append(outputs.JSON(**output_args['JSON']))

    # Screenshot: 戦績画面のスクリーンショットを保存します。
    if 'Screenshot' in output_plugins:
        OutputPlugins.append(
            outputs.Screenshot(**output_args['Screenshot']))

    # Slack: Slack 連携
    if 'Slack' in output_plugins:
        OutputPlugins.append(outputs.Slack(**output_args['Slack']))

    # StatInk: stat.ink (スプラトゥーンプレイ実績投稿サイト)
    if 'StatInk' in output_plugins:
        if opts.get('video_id'):
            output_args['StatInk']['video_id'] = opts['video_id']
        if opts.get('statink_payload'):
            output_args['StatInk']['payload_file'] = opts['statink_payload']

        OutputPlugins.append(outputs.StatInk(**output_args['StatInk']))

    # Twitter: Twitter 連携
    if 'Twitter' in output_plugins:
        OutputPlugins.append(outputs.Twitter(**output_args['Twitter']))

    # WebSocket サーバ
    if 'WebSocket' in output_plugins:
        OutputPlugins.append(outputs.WebSocket(**output_args['WebSocket']))

    # Video description for YouTube. It is expected to be used with
    # input.CVFile. Multiple matches in a video is not tested.
    #
    # YouTube 用、動画の概要。input.CVFile と組み合わせた使用を想定。
    # ビデオ内に複数のゲームがある場合には未検証。
    if (('Description' in output_plugins) or
            opts.get('output_description')):

        if opts.get('output_description'):
            output_args['Description']['output_filepath'] = (
                opts['output_description'])
        OutputPlugins.append(
            outputs.Description(**output_args['Description']))

    # 不具合調査向け。
    # イベントトリガをコンソールに出力。イベントトリガ時のスクリーンショット保存
    if 'DebugLog' in output_plugins:
        OutputPlugins.append(outputs.DebugLog(**output_args['DebugLog']))

    # 不具合調査向け。
    # ウインドウに対して v キー押下でデバッグ録画を開始する
    if 'DebugVideoWriter' in output_plugins:
        OutputPlugins.append(
            outputs.DebugVideoWriter(**output_args['DebugVideoWriter']))

    # PreviewDetected: 認識した画像をプレビュー上でマークする
    if 'PreviewDetected' in output_plugins:
        OutputPlugins.append(
            outputs.PreviewDetected(**output_args['PreviewDetected']))

    return OutputPlugins


def config(opts):
    # Checks if IkaConfig.py is an old version or not by checking the
    # existance of the IkaConfig class. If it is an old version,
    # we just use it to keep the backward compatibility.
    if hasattr(IkaConfig, 'IkaConfig'):
        return IkaConfig.IkaConfig().config(opts)

    # 使いたい入力を設定
    source = _init_source(opts)

    # Common configs among all sources.
    source_args = IkaConfig.SOURCE_ARGS

    # 一部のHDMIキャプチャはHDMIソースのピクセルがずれている。
    # 必要に応じてキャプチャのオフセットを(x, y) 指定
    if 'offset' in source_args:
        source.set_offset(source_args['offset'])

    # 処理するフレームレート数を制限する場合は下記の設定を行う
    # 経験上 10 フレーム/秒も処理できれば十分
    if 'frame_rate' in source_args:
        source.set_frame_rate(source_args['frame_rate'])

    # 使いたいプラグインを適宜設定
    OutputPlugins = _init_outputs(opts)

    # 入力ソース
    OutputPlugins.append(source)

    return [source, OutputPlugins]


if __name__ == '__main__':
    args = {}
    print(config(args))
