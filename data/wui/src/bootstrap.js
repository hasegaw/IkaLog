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

export function initBootstrap() {
    window.jQuery = require('jquery/dist/jquery.js');
    window.$ = window.jQuery;
    window.Tether = require('tether/dist/js/tether.js');
    
    require('bootstrap/dist/css/bootstrap.css');
    require('bootstrap/dist/js/bootstrap.js');
};

export function initFontAwesome() {
    require('font-awesome/css/font-awesome.min.css');
    require('font-awesome/fonts/fontawesome-webfont.eot');
    require('font-awesome/fonts/fontawesome-webfont.svg');
    require('font-awesome/fonts/fontawesome-webfont.ttf');
    require('font-awesome/fonts/fontawesome-webfont.woff');
    require('font-awesome/fonts/fontawesome-webfont.woff2');
    require('font-awesome/fonts/FontAwesome.otf');
};

export function initI18Next(defaultLang) {
    const i18next = require('i18next');
    const i18nextBackendXhr = require('i18next-xhr-backend');

    i18next
      .use(i18nextBackendXhr)
      .init({
        debug: (process.env.NODE_ENV !== 'production'),
        nsSeparator: '::',
        keySeparator: '..',
        lng: defaultLang,
        fallbackLng: false,
        ns: [
          'app',
          'sidebar',
          'input',
          'output-file',
          // 'output-sns',
          'output-statink',
          'output-speech',
          // 'output-autoit',
          // 'output-websocket',
        ],
        defaultNS: 'app',
        lowerCaseLng: true,
        preload: [ 'ja', 'en' ],
        escapeValue: false,
        backend: {
          loadPath: '/locales/{{lng}}.{{ns}}.json',
        },
      });
    return i18next;
};

export function initAppStyle() {
    require('./index.scss');
};
