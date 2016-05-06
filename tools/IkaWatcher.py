#!/usr/bin/env python3
# -*- coding: utf-8 -*-
#
#  IkaLog
#  ======
#  Copyright (C) 2016 Takeshi HASEGAWA
#  Copyright (C) 2016 Hiroyuki KOMATSU
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
#  ----
#
#  IkaWatcher is a watchdog of the specified directory. If the directory newly
#  has video files, IkaLog.py is triggered with the new video file.
#
#  This is an experimental implementation, only tested with AVT C875 on Mac.
#
#  Usage: ./tools/IkaWatcher.py --video_dir=~/Videos --video_ext=.avi
#
#  ----
#
#  This command additionally requires watchdog library.
#  https://pypi.python.org/pypi/watchdog

import argparse
import os.path
import queue
import subprocess
import threading
import time

from watchdog.events import FileSystemEventHandler
from watchdog.observers import Observer


def get_args():
    parser = argparse.ArgumentParser()
    parser.add_argument('--video_dir', '-d', dest='video_dir',
                        required=True, type=str)
    parser.add_argument('--video_ext', '-e', dest='video_ext',
                        default='.mp4', type=str)

    return vars(parser.parse_args())


def get_time(msec):
    return time.strftime("%Y%m%d_%H%M%S", time.localtime(msec))


def print_file_info(path):
    print('atime: %s' % get_time(os.path.getatime(path)))
    print('mtime: %s' % get_time(os.path.getmtime(path)))
    print('ctime: %s' % get_time(os.path.getctime(path)))
    print('size:  %s' % '{:,d}'.format(os.path.getsize(path)))
    print('')


def ikalog_with_queue(video_queue):
    ika_path = os.path.abspath(os.path.join(os.path.dirname(__file__), '..'))
    while True:
        video_path = video_queue.get()
        if video_path is None:
            break
        command = [os.path.join(ika_path, 'IkaLog.py'), '-f', video_path]
        subprocess.call(command)


class WatchdogHandler(FileSystemEventHandler):
    def __init__(self, video_queue, video_ext):
        super(WatchdogHandler, self).__init__()
        self._video_queue = video_queue
        self._video_ext = video_ext

    def on_created(self, event):
        path = event.src_path
        if not path.endswith(self._video_ext):
            return
        print('%s: on_created(%s)' % (get_time(time.time()), path))
        print_file_info(path)

    def on_modified(self, event):
        path = event.src_path
        if not path.endswith(self._video_ext):
            return
        print('%s: on_modified(%s)' % (get_time(time.time()), path))
        print_file_info(path)

        self._video_queue.put(path)

    def on_deleted(self, event):
        path = event.src_path
        if not path.endswith(self._video_ext):
            return
        print('%s: on_deleted(%s)' % (get_time(time.time()), path))


def main():
    video_queue = queue.Queue()
    args = get_args()

    video_dir = args['video_dir']
    video_ext = args['video_ext']

    watchdog_dir = os.path.expanduser(args['video_dir'])
    watchdog_handler = WatchdogHandler(video_queue, args['video_ext'])
    observer = Observer()
    observer.schedule(watchdog_handler, watchdog_dir, recursive=False)
    observer.start()

    ika_thread = threading.Thread(
        target=ikalog_with_queue, name='ikalog', args=(video_queue,))
    ika_thread.start()

    print('==== Started IkaWatcher ====')
    print('Automatically run IkaLog when the following files are created.')
    print('Target video files: %s' % os.path.join(video_dir, '*%s' % video_ext))

    try:
        while True:
            time.sleep(1)
    except KeyboardInterrupt:
        print('==== KeyboardInterrupt ====')
        observer.stop()
        video_queue.put(None)  # None in the queue stops ika_thread.
        ika_thread.join()


if __name__ in '__main__':
    main()
