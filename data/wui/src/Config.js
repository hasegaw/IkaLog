/*
 *  IkaLog
 *  ======
 *
 *  Copyright (C) 2015 Takeshi HASEGAWA
 *  Copyright (C) 2016 AIZAWA Hina
 *  
 *  Licensed under the Apache License, Version 2.0 (the "License");
 *  you may not use this file except in compliance with the License.
 *  You may obtain a copy of the License at
 *  
 *      http://www.apache.org/licenses/LICENSE-2.0
 *  
 *  Unless required by applicable law or agreed to in writing, software
 *  distributed under the License is distributed on an "AS IS" BASIS,
 *  WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
 *  See the License for the specific language governing permissions and
 *  limitations under the License.
 */

export function toIkaLogFormat(state) {
  const plugins = state.plugins;
  const payload = {};

  // input(Capture) {{{
  payload.Capture = (() => {
    const input = plugins.input;
    switch (input.driver) {
      case 'amarec':
        return {
          active_class: 'DirectShow',
          DirectShow: {
            source: 'AmaRec Video Capture',
          },
        };

      case 'directshow':
        return {
          active_class: 'DirectShow',
          DirectShow: input.device,
        };
        break;
      
      case 'avfoundation':
        return {
          active_class: 'AVFoundationCapture',
          AVFoundationCapture: input.device,
        };
        break;

      case 'opencv':
        return {
          active_class: 'CVCapture',
          CVCapture: input.device,
        };
        break;
    }
    return null;
  })();
  // }}}

  // CSV
  payload.CSV = (() => {
    const conf = plugins.output.csv;
    return {
      enabled: conf.enabled,
      filename: conf.path,
    };
  })();

  // JSON
  payload.JSON = (() => {
    const conf = plugins.output.json;
    return {
      enabled: conf.enabled,
      filename: conf.path,
    };
  })();

  // screenshot
  payload.Screenshot = (() => {
    const conf = plugins.output.screenshot;
    return {
      enabled: conf.enabled,
      dest_dir: conf.path,
    };
  })();

  // statink
  payload.StatInk = (() => {
    const conf = plugins.output.statink;
    return {
      enabled: conf.enabled,
      api_key: conf.apikey,
      show_response: conf.showResponse,
      track_inklings: conf.trackInklings,
      track_special_gauge: conf.trackSpecialGauge,
      track_special_weapon: conf.trackSpecialWeapon,
      track_objective: conf.trackObjective,
      track_splatzone: conf.trackSplatZone,
      anon_all: conf.anonymizer === 'all',
      anon_others: conf.anonymizer === 'others',
    };
  })();

  // boyomi
  payload.Boyomi = (() => {
    const conf = plugins.output.boyomi;
    return {
      enabled: conf.enabled,
      host: conf.host,
      port: conf.port,
    };
  })();

  return payload;
}
