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

export function getUILanguage(fallback = 'en') {
  let lang;
  if (_canUseLocalStorage()) {
    lang = window.localStorage.getItem('chrome.lang');
    if (lang && _isValidLangCode(lang)) {
      return lang;
    }
  }
  let langList = _getBrowserAcceptLanguages();
  for (let i = 0; i < langList.length; ++i) {
    lang = String(langList[i]).toLowerCase();
    const match = lang.match(/^([a-z]+)/);
    if (match) {
      if (_isValidLangCode(match[1])) {
        return match[1];
      }
    }
  }
  return fallback;
}

export function setUILanguage(lang) {
  if (!_isValidLangCode(lang)) {
    throw new Error(`${lang} is not valid language code.`);
  }
  if (!_canUseLocalStorage()) {
    console.warning('This browser does not support Local Storage technology.');
    return;
  }
  window.localStorage.setItem('chrome.lang', lang);
}

function _isValidLangCode(lang) {
  return lang === 'ja' || lang === 'en';
}

function _canUseLocalStorage() {
  return !!window.localStorage;
}

function _getBrowserAcceptLanguages() {
  let ret = [];
  const languages = window.navigator.languages;
  if (languages) {
    for (let i = 0; i < languages.length; ++i) {
      ret.push(languages[i]);
    }
  }
  if (window.navigator.userLanguage) {
    ret.push(window.navigator.userLanguage);
  }
  if (window.navigator.language) {
    ret.push(window.navigator.language);
  }
  return ret;
}

export function stopEvent(ev) {
  ev.preventDefault();
  ev.stopPropagation();
}
