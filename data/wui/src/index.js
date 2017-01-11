/*!
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

import React from 'react';
import ReactDOM from 'react-dom';
import App from './App';
import { initBootstrap, initFontAwesome, initI18Next, initAppStyle } from './bootstrap';
import { getUILanguage } from './Utils';
import endpoints from './endpoints';

initBootstrap();
initFontAwesome();
initAppStyle();

const initLang = getUILanguage('en');

const i18n = initI18Next(initLang);
window.i18n = i18n;
window.React = React;

const app = new App({
  renderer: el => {
    ReactDOM.render(el, document.getElementById('app-root'));
  },
  initialState: {
    tasks: {
      apply: null,
      screenshot: null,
    },
    chrome: {
      favicon: false,
      lang: 'unknown',
      content: 'preview',
      pluginTab: 'file',
      preview: null,
      lock: false, // true if communicating
      fatalError: false,
    },
    game: {
      lang: 'ja', // FIXME
    },
    system: null,
    // system: {
    //   hasBuiltinTwitterToken: true,
    //   isWindows: true,
    //   isMacOS: false,
    // },
    plugins: {
      input: null,
      // input: {
      //   driver: 'amarec',
      //   device: null,
      //   classes: {
      //     "AVFoundationCapture": [
      //       { "source": "Blackmagic" },
      //       { "source": "FaceTime HD Camera (Built-in)" },
      //     ],
      //     "CVCapture": [
      //     ],
      //   },
      // },
      output: null,
      // output: {
      //   csv: {
      //     enabled: false,
      //     path: 'C:\\path\\to\\file.csv',
      //   },
      //   json: {
      //     enabled: false,
      //     path: 'C:\\path\\to\\file.json',
      //   },
      //   screenshot: {
      //     enabled: false,
      //     path: 'C:\\path\\to\\directory',
      //   },
      //   twitter: {
      //     enabled: false,
      //     useReply: true,
      //     sendScreenShot: false,
      //     sendMyScore: false,
      //     sendKDRatio: false,
      //     sendRank: false,
      //     useKey: 'own', // 'own' or 'builtin'
      //     consumerKey: '',
      //     consumerSecret: '',
      //     accessToken: '',
      //     accessSecret: '',
      //     additionalMessage: '',
      //   },
      //   slack: {
      //     enabled: false,
      //     webhook: 'https://example.com/',
      //     botName: 'IkaLog',
      //   },
      //   statink: {
      //     enabled: false,
      //     apikey: '',
      //     showResponse: false,
      //     trackInklings: false,
      //     trackSpecialGauge: false,
      //     trackSpecialWeapon: false,
      //     trackObjective: false,
      //     trackSplatZone: false,
      //     anonymizer: false, // false, 'others', 'all'
      //   },
      //   boyomi: {
      //     enabled: false,
      //     host: '127.0.0.1',
      //     port: 50001,
      //   },
      //   mikumikumouth: {
      //     enabled: false,
      //     host: '127.0.0.1',
      //     port: 50082,
      //   },
      //   autoit: {
      //     enabled: false,
      //     rename: false,
      //     scriptPath: 'C:\\Path\\to\\Script.au3',
      //     outputPath: '',
      //   },
      //   websocket: {
      //     enabled: true,
      //     // host: '0.0.0.0',
      //     port: 9090,
      //   },
      // },
    },
  },
  middlewares: [
    t => {
      if (process.env.NODE_ENV !== 'production') {
        console.log(t);
      }
      return t;
    },
  ],
});
window.app = app;

i18n.on('loaded', opts => {
  app.emit('chrome:changelang', i18n.language);
});

app.update(x => x);
