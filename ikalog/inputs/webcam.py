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
import ctypes
import time
import threading

from ikalog.utils import *
from ikalog.inputs.filters.warp import warp
from ikalog.inputs.filters.deinterlace import deinterlace
from ikalog.inputs.filters.offset import offset
from ikalog.inputs.filters.white_balance import white_balance


# Needed in GUI mode
try:
    import wx
except:
    pass


class InputSourceEnumerator:

    def EnumWindows(self):
        numDevices = ctypes.c_int(0)
        r = self.dll.VI_Init()
        if (r != 0):
            return None

        r = self.dll.VI_GetDeviceNames(ctypes.pointer(numDevices))
        list = []
        for n in range(numDevices.value):
            friendly_name = self.dll.VI_GetDeviceName(n)
            list.append(friendly_name)

        self.dll.VI_Deinit()

        return list

    def EnumDummy(self):
        cameras = []
        for i in range(10):
            cameras.append('Input source %d' % (i + 1))

        return cameras

    def Enumerate(self):
        if IkaUtils.isWindows():
            try:
                cameras = self.EnumWindows()
                if len(cameras) > 1:
                    return cameras
            except:
                IkaUtils.dprint(
                    '%s: Failed to enumerate DirectShow devices' % self)

        return self.EnumDummy()

    def __init__(self):
        if IkaUtils.isWindows():
            videoinput_dll = os.path.join('lib', 'videoinput.dll')
            try:
                self.c_int_p = ctypes.POINTER(ctypes.c_int)

                ctypes.cdll.LoadLibrary(videoinput_dll)
                self.dll = ctypes.CDLL(videoinput_dll)

                self.dll.VI_Init.argtypes = []
                self.dll.VI_Init.restype = ctypes.c_int
                self.dll.VI_GetDeviceName.argtypes = [ctypes.c_int]
                self.dll.VI_GetDeviceName.restype = ctypes.c_char_p
                self.dll.VI_GetDeviceNames.argtypes = [self.c_int_p]
                self.dll.VI_GetDeviceNames.restype = ctypes.c_char_p
                self.dll.VI_GetDeviceName.argtypes = []
            except:
                IkaUtils.dprint(
                    "%s: Failed to initalize %s" % self, videoinput_dll)

class cvcapture:
    cap = None
    out_width = 1280
    out_height = 720
    need_resize = False
    need_deinterlace = False
    realtime = True
    offset = (0, 0)

    _systime_launch = int(time.time() * 1000)

    # アマレコTV のキャプチャデバイス名
    DEV_AMAREC = "AmaRec Video Capture"

    source = 'amarec'
    SourceDevice = None
    Deinterlace = False
    File = ''

    lock = threading.Lock()

    def enumerateInputSources(self):
        return InputSourceEnumerator().Enumerate()

    def read(self):
        if self.cap is None:
            return None, None

        self.lock.acquire()
        ret, frame = self.cap.read()
        self.lock.release()

        if not ret:
            return None, None

        if self.need_deinterlace:
            for y in range(frame.shape[0])[1::2]:
                frame[y, :] = frame[y - 1, :]

        if self.calibration_requested:
            self.filter_warp.calibrateWarp(frame)
            self.calibration_requested = False
            self.filter_warp.enable()

        frame = self.filter_warp.execute(frame)
        frame = self.filter_deinterlace.execute(frame)

        if self.calibration_requested_white_balance:
            self.filter_white_balance.calibrateColor(frame)
            self.calibration_requested_white_balance = False
            self.filter_white_balance.enable()

        frame = self.filter_offset.execute(frame)
        frame = self.filter_white_balance.execute(frame)

        t = None
        if not self.realtime:
            try:
                t = self.cap.get(cv2.CAP_PROP_POS_MSEC)
            except:
                pass
            if t is None:
                print('Cannot get video position...')
                self.realtime = True

        if self.realtime:
            t = int(time.time() * 1000) - self._systime_launch

        if self.need_resize:
            return cv2.resize(frame, (self.out_width, self.out_height)), t
        else:
            return frame, t

    def setResolution(self, width, height):
        self.cap.set(3, width)
        self.cap.set(4, height)
        self.need_resize = (width != self.out_width) or (
            height != self.out_height)

    def initCapture(self, source, width=1280, height=720):
        self.lock.acquire()
        if not self.cap is None:
            self.cap.release()

        self.cap = cv2.VideoCapture(source)
        self.setResolution(width, height)
        self.lock.release()

    def isWindows(self):
        try:
            os.uname()
        except AttributeError:
            return True

        return False

    def startCamera(self, source_name):

        try:
            source = int(source_name)
        except:
            IkaUtils.dprint('%s: Looking up device name %s' %
                            (self, source_name))
            try:
                source_name = source_name.encode('utf-8')
            except:
                pass

            try:
                source = self.enumerateInputSources().index(source_name)
            except:
                IkaUtils.dprint("%s: Input '%s' not found" %
                                (self, source_name))
                return False

        IkaUtils.dprint('%s: initalizing capture device %s' % (self, source))
        self.realtime = True
        if self.isWindows():
            self.initCapture(700 + source)
        else:
            self.initCapture(0 + source)

    def startRecordedFile(self, file):
        IkaUtils.dprint(
            '%s: initalizing pre-recorded video file %s' % (self, file))
        self.realtime = False
        self.initCapture(file)

    def restartInput(self):
        IkaUtils.dprint('RestartInput: source %s file %s device %s' %
                        (self.source, self.File, self.SourceDevice))

        if self.source == 'camera':
            self.startCamera(self.SourceDevice)

        elif self.source == 'file':
            self.startRecordedFile(self.File)
        else:
            # Use amarec if available
            self.source = 'amarec'

        if self.source == 'amarec':
            self.startCamera(self.DEV_AMAREC)

        success = True
        if self.cap is None:
            success = False

        if success:
            if not self.cap.isOpened():
                success = False

        return success

    def onKeyPress(self, context, key):
        if (key == ord('c') or key == ord('C')):
            # 次回キャリブレーションを行う
            self.calibration_requested = True

        if (key == ord('d')):
            self.filter_deinterlace.enabled = not self.filter_deinterlace.enabled

        if key == ord('w'):
            self.calibration_requested_white_balance = True

        if key == ord('h'):
            self.filter_offset.offset = (self.filter_offset.offset[0] - 1, self.filter_offset.offset[1] + 0)

        if key == ord('j'):
            self.filter_offset.offset = (self.filter_offset.offset[0] + 0, self.filter_offset.offset[1] + 1)

        if key == ord('k'):
            self.filter_offset.offset = (self.filter_offset.offset[0] + 0, self.filter_offset.offset[1] - 1)

        if key == ord('l'):
            self.filter_offset.offset = (self.filter_offset.offset[0] + 1, self.filter_offset.offset[1] + 0)


    def __init__(self, debug=False):
        self.debug = debug
        self.calibration_requested = False
        self.calibration_requested_white_balance = False
        self.warp_mode = False
        self.filter_warp = warp(self)
        self.filter_deinterlace = deinterlace(self)
        self.filter_offset = offset(self)
        self.filter_offset.enable()
        self.filter_white_balance = white_balance(self)
        self.filter_white_balance.enable()

if __name__ == "__main__":
    obj = cvcapture()

    list = InputSourceEnumerator().Enumerate()
    for n in range(len(list)):
        print("%d: %s" % (n, list[n]))

    dev = input("Please input number (or name) of capture device: ")

    obj.startCamera(dev)

    k = 0
    while k != 27:
        frame, t = obj.read()
        cv2.imshow(obj.__class__.__name__, frame)
        k = cv2.waitKey(1)
        obj.onKeyPress(None, k)
