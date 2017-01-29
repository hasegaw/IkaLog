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

import React from 'react';
import { Component } from 'flumpt';

const t = text => window.i18n.t(text, {ns: 'sidebar'});

export default class LangBox extends Component {
  render() {
    return (
      <div className="card mb-3">
        <div className="card-header">
          Language
        </div>
        <div className="card-block">
          <UiLang {...this.props} />
          <GameLang {...this.props} />
        </div>
      </div>
    );
  }
}

class UiLang extends Component {
  render() {
    return (
      <div className="mb-3">
        <p className="mb-0">
          IkaLog UI:
        </p>
        <div className="btn-group-vertical btn-block">
          <UiButton text="日本語" target="ja" {...this.props} />
          <UiButton text="English" target="en" {...this.props} />
        </div>
      </div>
    );
  }
}

class GameLang extends Component {
  render() {
    return (
      <div className="mb-0">
        <p className="mb-0">
          {t('Your copy of Splatoon')}:
        </p>
        <div className="btn-group-vertical btn-block">
          <GameButton {...this.props} />
        </div>
      </div>
    );
  }
}

class UiButton extends Component {
  constructor(props) {
    super(props);
    this._onClick = this._onClick.bind(this);
  }

  render() {
    const selected = this.props.target === this.props.chrome.lang;
    const classes = 'btn btn-block ' + (selected ? 'btn-info active' : 'btn-secondary');
    return (
      <button type="button" className={classes} onClick={this._onClick}>
        {this.props.text}
      </button>
    );
  }

  _onClick() {
    this.dispatch('chrome:changelang', this.props.target);
  }
}

class GameButton extends Component {
  render() {
    return (
      <button type="button" className="btn btn-block btn-info active">
        {t(this.getLang())}
      </button>
    );
  }

  getLang() {
    const langs = this.props.system.gameLanguages || [];
    for (let i = 0; i < langs.length; ++i) {
      const lang = String(langs[i]).toLowerCase().replace(/[^a-z0-9]+/, '_');
      switch (lang) {
        case 'ja':
        case 'ja_jp':
          return 'Japanese';

        case 'en_na':
          return 'English (NA)';

        case 'en_eu':
          return 'English (EU)';
      }
    }
    return "Unknown";
  }
}
