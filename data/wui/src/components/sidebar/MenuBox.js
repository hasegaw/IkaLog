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

export default class MenuBox extends Component {
  render() {
    return (
      <div className="card mb-1" id="menu">
        <div className="card-header hidden-sm-up">
          {t('Menu')}
        </div>
        <div className="card-block">
          <Buttons {...this.props} />
          <Apply {...this.props} />
        </div>
      </div>
    );
  }
}

class Buttons extends Component {
  render() {
    return (
      <div className="btn-group-vertical btn-block mb-2">
        <Button text="Preview" target="preview" {...this.props} />
        <Button text="Video Input" target="input" {...this.props} />
        <Button text="Plugins" target="output" {...this.props} />
      </div>
    );
  }
}

class Button extends Component {
  constructor(props) {
    super(props);
    this._onClick = this._onClick.bind(this);
  }

  render() {
    const selected = this.props.target === this.props.chrome.content;
    const classes = 'btn ' + (selected ? 'btn-info active' : 'btn-secondary');
    return (
      <button type="button" className={classes} onClick={this._onClick}>
        {t(this.props.text)}
        <span className="fa fa-fw fa-angle-right" />
      </button>
    );
  }

  _onClick() {
    this.dispatch('chrome:changeContent', this.props.target);
  }
}

class Apply extends Component {
  constructor(props) {
    super(props);
    this._onClick = this._onClick.bind(this);
  }

  render() {
    if (this.props.tasks.apply === null) {
      return (
        <div className="text-right text-xs-right">
          <button type="button" className="btn btn-outline-primary" onClick={this._onClick}>
            <span className="fa fa-check fa-fw"/>
            {t('Apply')}
          </button>
        </div>
      );
    } else {
      return (
        <div className="text-right text-xs-right">
          <button type="button" className="btn btn-outline-primary" disabled="disabled">
            <span className="fa fa-fw fa-circle-o-notch fa-spin"/>
            {t('Applying')}
          </button>
        </div>
      );
    }
  }

  _onClick() {
    this.dispatch(':saveConfig', this.props.target);
  }
}
