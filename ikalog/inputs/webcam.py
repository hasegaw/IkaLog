#!/usr/bin/env python3
# -*- coding: utf-8 -*-
#
#  IkaLog
#  ======
#  Copyright (C) 2015 Hiromichi Itou
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

#
#  This source includes modified version of sample codes in OpenCV
#  distribution, licensed under 3-clause BSD License.
#
# By downloading, copying, installing or using the software you agree to this license.
# If you do not agree to this license, do not download, install,
# copy or use the software.
#
#
#                           License Agreement
#                For Open Source Computer Vision Library
#                        (3-clause BSD License)
#
# Copyright (C) 2000-2015, Intel Corporation, all rights reserved.
# Copyright (C) 2009-2011, Willow Garage Inc., all rights reserved.
# Copyright (C) 2009-2015, NVIDIA Corporation, all rights reserved.
# Copyright (C) 2010-2013, Advanced Micro Devices, Inc., all rights reserved.
# Copyright (C) 2015, OpenCV Foundation, all rights reserved.
# Copyright (C) 2015, Itseez Inc., all rights reserved.
# Third party copyrights are property of their respective owners.
#
# Redistribution and use in source and binary forms, with or without modification,
# are permitted provided that the following conditions are met:
#
#   * Redistributions of source code must retain the above copyright notice,
#     this list of conditions and the following disclaimer.
#
#   * Redistributions in binary form must reproduce the above copyright notice,
#     this list of conditions and the following disclaimer in the documentation
#     and/or other materials provided with the distribution.
#
#   * Neither the names of the copyright holders nor the names of the contributors
#     may be used to endorse or promote products derived from this software
#     without specific prior written permission.
#
# This software is provided by the copyright holders and contributors "as is" and
# any express or implied warranties, including, but not limited to, the implied
# warranties of merchantability and fitness for a particular purpose are disclaimed.
# In no event shall copyright holders or contributors be liable for any direct,
# indirect, incidental, special, exemplary, or consequential damages
# (including, but not limited to, procurement of substitute goods or services;
# loss of use, data, or profits; or business interruption) however caused
# and on any theory of liability, whether in contract, strict liability,
# or tort (including negligence or otherwise) arising in any way out of
# the use of this software, even if advised of the possibility of such damage.
#

import ctypes
import time
import threading
import pickle

from ikalog.utils import *

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


class webcam:
    cap = None
    out_width = 1280
    out_height = 720
    realtime = True
    offset = (0, 0)

    _systime_launch = int(time.time() * 1000)

    source = 'camera'
    SourceDevice = None
    Deinterlace = False
    File = ''

    lock = threading.Lock()

    def enumerateInputSources(self):
        return InputSourceEnumerator().Enumerate()

    def offsetImage(self, img):
        if (self.offset[0] == 0 and self.offset[1] == 0):
            return None

        ox = self.offset[0]
        oy = self.offset[1]

        sx1 = max(-ox, 0)
        sy1 = max(-oy, 0)

        dx1 = max(ox, 0)
        dy1 = max(oy, 0)

        w = min(self.out_width - dx1, self.out_width - sx1)
        h = min(self.out_height - dy1, self.out_height - sy1)

        new_frame = np.zeros((out_height, out_width, 3), np.uint8)
        new_frame[dy1:dy1 + h, dx1:dx1 + w] = frame[sy1:sy1 + h, sx1:sx1 + w]
        return new_frame

    def getVideoTime(self):
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

        return t

    def filter_matches(self, kp1, kp2, matches, ratio=0.75):
        mkp1, mkp2 = [], []
        for m in matches:
            if len(m) == 2 and m[0].distance < m[1].distance * ratio:
                m = m[0]
                mkp1.append(kp1[m.queryIdx])
                mkp2.append(kp2[m.trainIdx])
        p1 = np.float32([kp.pt for kp in mkp1])
        p2 = np.float32([kp.pt for kp in mkp2])
        kp_pairs = zip(mkp1, mkp2)
        return p1, p2, kp_pairs

    #
    # Color balance calibration and filtering
    #
    def getColorBalance(self, img):
        r = (1052, 41, 70, 41)
        white = img[r[1]:r[1] + r[3], r[0]: r[0] + r[2], :]

        avg_b = np.average(white[:, :, 0]) * 1.0
        avg_g = np.average(white[:, :, 1]) * 1.0
        avg_r = np.average(white[:, :, 2]) * 1.0

        avg = np.average(white)

        coff_b = (avg / avg_b)
        coff_g = (avg / avg_g)
        coff_r = (avg / avg_r)

        return avg, (avg_b, avg_g, avg_r), (coff_b, coff_g, coff_r)

    def filterImage(self, img, coffs):
        img_work = np.array(img, np.float32)

        for n in range(len(coffs)):
            img_work[:, :, n] = img_work[:, :, n] * coffs[n]
            img_work[img_work > 255] = 255

        return np.array(img_work, np.uint8)

    def calibrateColor(self, capture_image):
        img_720p = cv2.resize(capture_image, (1280, 720))
        avg, avgs, coffs = self.getColorBalance(img_720p)
        print('source avg', avg, avgs)
        print('source coff', coffs)

        # HDMI input sample (reference image)
        #img_hdmi = cv2.imread('camera/color_balance/pause_hdmi.bmp')
        #img_hdmi_720p = cv2.resize(img_hdmi, (1280, 720))
        #avg_hdmi, avgs_hdmi, coffs_hdmi = self.getColorBalance(img_hdmi_720p)
        #
        #print('HDMI   avg', avg_hdmi, avgs_hdmi)
        #print('HDMI   coff', coffs_hdmi)
        avg_hdmi = 233.203252033

        # gain
        coffs_with_gain = (
            coffs[0] * avg_hdmi / avg,
            coffs[1] * avg_hdmi / avg,
            coffs[2] * avg_hdmi / avg,
        )

        img_out = self.filterImage(img_720p, coffs_with_gain)
        avg_out, avgs_out, coffs_out = self.getColorBalance(img_out)

        print('output avg', avg_out)

        self.white_filter_coffs = coffs_with_gain

    #
    # Warp calibration
    #

    def calibrateWarp(self, capture_image):
        capture_image_gray = cv2.cvtColor(capture_image, cv2.COLOR_BGR2GRAY)

        capture_image_keypoints, capture_image_descriptors = self.detector.detectAndCompute(
            capture_image_gray, None)
        print('caputure_image - %d features' % (len(capture_image_keypoints)))

        print('matching...')

        raw_matches = self.matcher.knnMatch(
            self.calibration_image_descriptors,
            trainDescriptors=capture_image_descriptors,
            k=2
        )
        p1, p2, kp_pairs = self.filter_matches(
            self.calibration_image_keypoints,
            capture_image_keypoints,
            raw_matches,
        )

        if len(p1) >= 4:
            H, status = cv2.findHomography(p1, p2, cv2.RANSAC, 5.0)
            print('%d / %d  inliers/matched' % (np.sum(status), len(status)))
        else:
            H, status = None, None
            print('%d matches found, not enough for homography estimation' % len(p1))
            self.calibration_requested = False
            return False

        if H is None:
            # Should never reach there...
            self.calibration_requested = False
            return False

        calibration_image_height, calibration_image_width = self.calibration_image_size

        corners = np.float32(
            [[0, 0],
             [calibration_image_width, 0],
             [calibration_image_width, calibration_image_height],
             [0, calibration_image_height]]
        )

        pts1 = np.float32(cv2.perspectiveTransform(
            corners.reshape(1, -1, 2), H).reshape(-1, 2) + (0, 0))

        IkaUtils.dprint('pts1: %s' % [pts1])
        IkaUtils.dprint('pts2: %s' % [self.pts2])

        self.M = cv2.getPerspectiveTransform(pts1, self.pts2)

        self.warp_mode = True
        self.calibration_requested = False
        self.last_calibration_time = time.time()

        return True

    def warpImage(self, frame):
        return cv2.warpPerspective(frame, self.M, (1280, 720))

    def tuples2keyPoints(self, tuples):
        new_l = []
        for point in tuples:
            pt, size, angle, response, octave, class_id = point
            new_l.append(cv2.KeyPoint(
                pt[0], pt[1], size, angle, response, octave, class_id))
        return new_l

    def keyPoints2tuples(self, points):
        new_l = []
        for point in points:
            new_l.append((point.pt, point.size, point.angle, point.response, point.octave,
                          point.class_id))
        return new_l

    def loadModelFromFile(self, file):
        f = open(file, 'rb')
        l = pickle.load(f)
        f.close()
        self.calibration_image_size = l[0]
        self.calibration_image_keypoints = self.tuples2keyPoints(l[1])
        self.calibration_image_descriptors = l[2]

    def saveModelToFile(self, file):
        f = open(file, 'wb')
        pickle.dump([
            self.calibration_image_size,
            self.keyPoints2tuples(self.calibration_image_keypoints),
            self.calibration_image_descriptors,
        ], f)
        f.close()

    def initializeCalibration(self):
        # Calibration stuff.
        model_filename = os.path.join(
            IkaUtils.baseDirectory(), 'data', 'webcam_calibration.model')
        print(model_filename)

        self.detector = cv2.AKAZE_create()
        self.norm = cv2.NORM_HAMMING
        self.matcher = cv2.BFMatcher(self.norm)

        self.loadModelFromFile(model_filename)
        IkaUtils.dprint('%s: Loaded model data')
        try:
            IkaUtils.dprint('%s: Loaded model data')
        except:

            calibration_image = cv2.imread('camera/ika_usbcam/Pause.png', 0)
            self.calibration_image_size = calibration_image.shape[:2]
            calibration_image_hight, calibration_image_width = calibration_image.shape[
                :2]

            self.calibration_image_keypoints, self.calibration_image_descriptors = self.detector.detectAndCompute(
                calibration_image, None)
            print(self.calibration_image_keypoints)
            print(self.calibration_image_descriptors)

            self.saveModelToFile(model_filename)
            IkaUtils.dprint('%s: Created model data')

        print('calibration_image - %d features' %
              (len(self.calibration_image_keypoints)))

        self.pts2 = np.float32([[0, 0], [1280, 0], [1280, 720], [0, 720]])
        self.M = cv2.getPerspectiveTransform(self.pts2, self.pts2)

    #
    # input plugin implemation
    #

    def read(self):
        if self.cap is None:
            return None, None

        self.lock.acquire()
        ret, frame = self.cap.read()
        self.lock.release()

        if not ret:
            return None, None

        self.last_raw_frame = frame.copy()

        calibrate_color = False
        if self.calibration_requested:
            calibrate_color = self.calibrateWarp(frame)

        if self.warp_mode:
            frame = self.warpImage(frame)

        offset_frame = self.offsetImage(frame)
        if not offset_frame is None:
            self.last_pre_offset_frame = frame
            frame = offset_frame

        if calibrate_color and self.enableWhiteColorCalibration:
            self.calibrateColor(frame)
            print(self.white_filter_coffs)

            if max(self.white_filter_coffs) > 2.2 or min(self.white_filter_coffs) < 0.8:
                IkaUtils.dprint(
                    '%s: White balance failed. probaby warp calibration failure. trying...' % self)
                self.white_filter_coffs = None
#                self.calibration_requested = True
                self.warp_mode = False

        if self.white_filter_coffs:
            self.last_pre_filter_frame = frame
            frame = self.filterImage(frame, self.white_filter_coffs)

        self.last_frame = frame

        frame_final = cv2.resize(frame, (self.out_width, self.out_height))

        if self.debug:
            # img_hdmi is available only in development site.
            try:
                frame_with_mask = cv2.cvtColor(frame_final, cv2.COLOR_BGR2GRAY)
                frame_with_mask = abs(
                    frame_with_mask - cv2.cvtColor(self.img_hdmi, cv2.COLOR_BGR2GRAY))
                cv2.imshow('frame_with_mask', cv2.resize(
                    frame_with_mask, (640, 320)))
            except:
                pass

            cv2.imshow('camera', cv2.resize(self.last_raw_frame, (640, 320)))

        t = self.getVideoTime()
        return frame_final, t

    def setResolution(self, width, height):
        self.cap.set(3, width)
        self.cap.set(4, height)

    def initCapture(self, source, width=1280, height=720):
        self.lock.acquire()
        if not self.cap is None:
            self.cap.release()

        self.cap = cv2.VideoCapture(source)
        #self.setResolution(width, height)
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

        if self.source == 'file':
            self.startRecordedFile(self.File)
        else:
            self.source = 'camera'

        if self.source == 'camera':
            self.startCamera(self.SourceDevice)

        success = True
        if self.cap is None:
            success = False

        if success:
            if not self.cap.isOpened():
                success = False

        return success

    def ApplyUI(self):
        self.source = ''
        for control in [self.radioCamera, self.radioFile]:
            if control.GetValue():
                self.source = {
                    self.radioCamera: 'camera',
                    self.radioFile: 'file',
                }[control]

        self.SourceDevice = self.listCameras.GetItems(
        )[self.listCameras.GetSelection()]
        self.File = self.editFile.GetValue()
        self.Deinterlace = self.checkDeinterlace.GetValue()

        # この関数は GUI 動作時にしか呼ばれない。カメラが開けなかった
        # 場合にメッセージを出す
        if not self.restartInput():
            r = wx.MessageDialog(None, u'キャプチャデバイスの初期化に失敗しました。設定を見直してください', 'Error',
                                 wx.OK | wx.ICON_ERROR).ShowModal()
            IkaUtils.dprint(
                "%s: failed to activate input source >>>>" % (self))
        else:
            IkaUtils.dprint("%s: activated new input source" % self)

    def RefreshUI(self):
        if self.source == 'camera':
            self.radioCamera.SetValue(True)

        if self.source == 'file':
            self.radioFile.SetValue(True)

        try:
            dev = self.SourceDevice
            index = self.listCameras.GetItems().index(dev)
            self.listCameras.SetSelection(index)
        except:
            IkaUtils.dprint('Current configured device is not in list')

        if not self.File is None:
            self.editFile.SetValue('')
        else:
            self.editFile.SetValue(self.File)

        self.checkDeinterlace.SetValue(self.Deinterlace)

    def onConfigReset(self, context=None):
        # さすがにカメラはリセットしたくないな
        pass

    def onConfigLoadFromContext(self, context):
        self.onConfigReset(context)
        try:
            conf = context['config']['cvcapture']
        except:
            conf = {}

        self.source = ''
        try:
            if conf['Source'] in ['camera', 'file', u'camera', u'file']:
                self.source = conf['Source']
        except:
            pass

        if 'SourceDevice' in conf:
            try:
                self.SourceDevice = conf['SourceDevice']
            except:
                # FIXME
                self.SourceDevice = 0

        if 'File' in conf:
            self.File = conf['File']

        if 'Deinterlace' in conf:
            self.Deinterlace = conf['Deinterlace']

        self.RefreshUI()
        return self.restartInput()

    def onConfigSaveToContext(self, context):
        context['config']['cvcapture'] = {
            'Source': self.source,
            'File': self.File,
            'SourceDevice': self.SourceDevice,
            'Deinterlace': self.Deinterlace,
        }

    def onConfigApply(self, context):
        self.ApplyUI()

    def OnReloadDevicesButtonClick(self, event=None):
        cameras = self.enumerateInputSources()
        self.listCameras.SetItems(cameras)
        try:
            index = self.enumerateInputSources().index(self.SourceDevice)
            self.listCameras.SetSelection(index)
        except:
            IkaUtils.dprint('Error: Device not found')

    def onOptionTabCreate(self, notebook):
        self.panel = wx.Panel(notebook, wx.ID_ANY)
        self.page = notebook.InsertPage(0, self.panel, 'Input')

        cameras = self.enumerateInputSources()

        self.layout = wx.BoxSizer(wx.VERTICAL)
        self.panel.SetSizer(self.layout)

        self.radioCamera = wx.RadioButton(
            self.panel, wx.ID_ANY, u'Realtime Capture from HDMI grabber')
        self.radioCamera.SetValue(True)
        self.radioFile = wx.RadioButton(
            self.panel, wx.ID_ANY, u'Read from pre-recorded video file (for testing)')
        self.editFile = wx.TextCtrl(self.panel, wx.ID_ANY, u'hoge')
        self.listCameras = wx.ListBox(self.panel, wx.ID_ANY, choices=cameras)
        self.listCameras.SetSelection(0)
        self.buttonReloadDevices = wx.Button(
            self.panel, wx.ID_ANY, u'Reload Devices')
        self.checkDeinterlace = wx.CheckBox(
            self.panel, wx.ID_ANY, u'Enable Deinterlacing (experimental)')

        self.layout.Add(wx.StaticText(
            self.panel, wx.ID_ANY, u'Select Input source:'))
        self.layout.Add(self.radioCamera)
        self.layout.Add(self.listCameras, flag=wx.EXPAND)
        self.layout.Add(self.buttonReloadDevices)
        self.layout.Add(self.radioFile)
        self.layout.Add(self.editFile, flag=wx.EXPAND)
        self.layout.Add(self.checkDeinterlace)
        self.layout.Add(wx.StaticText(self.panel, wx.ID_ANY, u'Video Offset'))

        self.buttonReloadDevices.Bind(
            wx.EVT_BUTTON, self.OnReloadDevicesButtonClick)

    def onKeyPress(self, context, key):
        if not (key == ord('c') or key == ord('C')):
            return False

        # 次回キャリブレーションを行う
        self.calibration_requested = True

    def __init__(self, debug=False):
        self.img_hdmi = cv2.imread('camera/color_balance/pause_hdmi.bmp')
        self.debug = debug
        self.enableWhiteColorCalibration = False

        # Whether user(or application request webcam calibration)
        self.calibration_requested = False

        # Whether this input is webcam mode and apply warp.
        self.warp_mode = False

        # Unix time last calibration was performed.
        self.last_calibration_time = 0

        # last raw frame, without any modification.
        self.last_raw_frame = None

        # last frame, before offseting.
        self.last_pre_offset_frame = None

        # last frame that read() returned to the application.
        self.last_frame = None

        # White color calibration coefficient parameters. None = no filtering
        self.white_filter_coffs = None
        self.initializeCalibration()

if __name__ == "__main__":
    obj = webcam()

    list = InputSourceEnumerator().Enumerate()
    for n in range(len(list)):
        print("%d: %s" % (n, list[n]))

    if len(sys.argv) > 1:
        obj.startRecordedFile(sys.argv[1])
    else:
        dev = input("Please input number (or name) of capture device: ")
        obj.startCamera(dev)

    k = 0
    while k != 27:
        frame, t = obj.read()
        cv2.imshow(obj.__class__.__name__, frame)
        k = cv2.waitKey(1)
        obj.onKeyPress(None, k)
