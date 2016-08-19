;
;  IkaLog
;  ======
;  Copyright (C) 2015 Takeshi HASEGAWA
;
;  Licensed under the Apache License, Version 2.0 (the 'License');
;  you may not use this file except in compliance with the License.
;  You may obtain a copy of the License at
;
;      http://www.apache.org/licenses/LICENSE-2.0
;
;  Unless required by applicable law or agreed to in writing, software
;  distributed under the License is distributed on an 'AS IS' BASIS,
;  WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
;  See the License for the specific language governing permissions and
;  limitations under the License.

;
;  Start and stop recording using Open Broadcaster Software(OBS).
;
;  To Start Recording:
;    ControlOBS.au3 start
;
;  To Stop Recording:
;    ControlOBS.au3 stop
;
;  To Reanem the recording:
;    If you want to rename the recording to a specific filename,
;    Specifcy the filename as environment variables
;    IKALOG_MP4_DESTDIR and IKALOG_MP4_DESTNAME.
;
;  Though this script will sleep seconds so that work on
;  a specific environment. The behavior is subject to change.
;

#include <FileConstants.au3>
#include <StringConstants.au3>


;環境と好みに合わせて値を設定してください。
Const $STARTsleepSec = 0    ;録画開始の待機時間（秒で指定）
Const $STOPsleepSec = 10    ;録画終了の待機時間（秒で指定）
Const $RENAMEsleepSec = 3   ;録画終了後リネーム処理までの待機時間（秒で指定）


Func RenameFile($source)
	Local $dest = EnvGet('IKALOG_MP4_DESTNAME')
	$dest = StringReplace($dest, "/", "\")
	If $dest = '' Then
		Return False
	EndIf

	FileMove($source, $dest, $FC_OVERWRITE)
EndFunc	

Func FindRecentRecording()
	Local $directory = EnvGet('IKALOG_MP4_DESTDIR')

	; Replace all slashes to backslashes.
	; $directory also needs a backslash at its end.
	$directory = StringReplace($directory, "/", "\")
	If StringRight($directory, 1) <> "\" Then
		$directory = $directory & "\"
	EndIf

	Local $hSearch = FileFindFirstFile($directory & '*.mp4')

	If $hSearch = -1 Then
		Return False
	EndIf

	Local $latest_file = ''
	Local $latest_timestamp = ''

	While True
		Local $file = FileFindNextFile($hSearch)
		If @error Then ExitLoop

		Local $timestamp = FileGetTime($directory & $file, $FT_MODIFIED, $FT_STRING)
		If StringCompare($timestamp, $latest_timestamp) > 0 Then
			$latest_file = $directory & $file
			$latest_timestamp = $timestamp
		EndIf
	WEnd

	FileClose($hSearch)

	If $latest_file = '' Then
		Return False
	EndIf

	Return $latest_file
EndFunc

Func ControlOBS($stop)
    Local $hWnd = WinWait('[CLASS:OBSWindowClass]', '', 1)

	If $hWnd == 0 Then
		Return False
	EndIf

	; Get current state.
	Local $l = ControlGetText ($hWnd, '', 'Button5')

	Local $inRecording_ja = (StringCompare($l, '録画停止') == 0)
	Local $inRecording_en = (StringCompare($l, 'Stop Recording') == 0)
	Local $inRecording = $inRecording_ja or $inRecording_en

	Local $click = False
	If $inRecording and $stop Then
		# Stop Recording.
		$click = True
	ElseIf (Not $inRecording) and (Not $stop) Then
		# Start Recording.
		$click = True
	EndIf

	If $click Then
		If $stop Then
			; 録画終了待機
			Sleep(1000 * $STOPsleepSec)
		Else
			; 録画開始待機
			Sleep(1000 * $STARTsleepSec)
		EndIf

		ControlClick($hWnd, '', 'Button5')

		If $stop Then
			Sleep(1000 * $RENAMEsleepSec)
			Local $file  = FindRecentRecording()
			RenameFile($file)
		EndIf
	EndIf
EndFunc


Func DetectOBSMultiPlatform()
    Local $hWnd = WinWait('[CLASS:Qt5QWindowIcon;REGEXPTITLE:OBS\s]', '', 1)

	If $hWnd == 0 Then
		Return False
	EndIf

    Return True
EndFunc



if ($CmdLine[0] = 0) Then	;exeにコンバートした時 確認に便利かなと考え追加
   Local $msg = StringFormat("%s%s",     "--- 起動オプション---", @LF)
   $msg = StringFormat("%s%s%s%s%s",$msg, "録画開始:", @ScriptName, " start", @LF)
   $msg = StringFormat("%s%s%s%s", $msg, "録画終了:", @ScriptName, " stop" & @LF & @LF)
   $msg = StringFormat("%s%s%s",    $msg, "--- 現在の設定 --- ", @LF)
   $msg = StringFormat("%s録画開始の待機時間 %s秒%s", $msg, $STARTsleepSec, @LF)
   $msg = StringFormat("%s録画終了の待機時間 %s秒%s", $msg, $STOPsleepSec,  @LF)
   $msg = StringFormat("%sリネームの待機時間 %s秒%s", $msg, $RENAMEsleepSec, @LF)
   MsgBox(64, "起動オプション & 現在の設定", $msg)

   if (DetectOBSMultiPlatform()) Then
       MsgBox(64, "Detected OBS Multiplatform", "This script supports OBS Classic only")
   EndIf

Else
   $stop = StringCompare($CmdLine[1], 'stop') == 0
   ControlOBS($stop)
EndIf
