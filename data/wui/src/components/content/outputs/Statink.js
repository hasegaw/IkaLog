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
import { Checkbox, LabeledInput, RadioButton, WrappedCheckbox, WrappedRadioButton } from '../../elements';

const INDENT = 'offset-1 col-11';
const t = (text) => window.i18n.t(text, {ns: 'output-statink'});

export default class Twitter extends Component {
  constructor(props) {
    super(props);
    this._onChangeEnable = this._onChangeEnable.bind(this);
    this._onToggleFlag = this._onToggleFlag.bind(this);
  }

  render() {
    const input = this.props.plugins.output.statink.enabled ? this._renderInput() : null;

    return (
      <fieldset>
        <legend>
          {t('stat.ink')}
          <small>
            <a href="https://stat.ink/" target="_blank">
              <span className="fa fa-fw fa-external-link" />
            </a>
          </small>
        </legend>
        <div className="form-group">
          <Checkbox
              name="output-statink-enable"
              checked={!!this.props.plugins.output.statink.enabled}
              text={t('Post game results to stat.ink')}
              onChange={this._onChangeEnable}
            />
        </div>
        {input}
      </fieldset>
    );
  }

  _renderInput() {
    return (
      <div className={INDENT}>
        <ApiKey {...this.props} />
        <WrappedCheckbox
            name="output-statink-chk1"
            checked={!!this.props.plugins.output.statink.showResponse}
            text={t('Show stat.ink response in console')}
            onChange={e => this._onToggleFlag(e, 'showResponse')}
          />
        <WrappedCheckbox
            name="output-statink-chk2"
            checked={!!this.props.plugins.output.statink.trackInklings}
            text={t('Include inkling status (experimental)')}
            onChange={e => this._onToggleFlag(e, 'trackInklings')}
          />
        <WrappedCheckbox
            name="output-statink-chk3"
            checked={!!this.props.plugins.output.statink.trackSpecialGauge}
            text={t('Include Special gauge (experimental)')}
            onChange={e => this._onToggleFlag(e, 'trackSpecialGauge')}
          />
        <WrappedCheckbox
            name="output-statink-chk4"
            checked={!!this.props.plugins.output.statink.trackSpecialWeapon}
            text={t('Include Special Weapons (experimental)')}
            onChange={e => this._onToggleFlag(e, 'trackSpecialWeapon')}
          />
        <WrappedCheckbox
            name="output-statink-chk5"
            checked={!!this.props.plugins.output.statink.trackObjective}
            text={t('Include position data of tracked objectives (experimental)')}
            onChange={e => this._onToggleFlag(e, 'trackObjective')}
          />
        <WrappedCheckbox
            name="output-statink-chk6"
            checked={!!this.props.plugins.output.statink.trackSplatZone}
            text={t('Include SplatZone counters (experimental)')}
            onChange={e => this._onToggleFlag(e, 'trackSplatZone')}
          />
        <Anonymizer {...this.props} />
      </div>
    );
  }

  _onChangeEnable() {
    this.dispatch('output:changeStatinkEnable', !this.props.plugins.output.statink.enabled);
  }

  _onToggleFlag(e, flag) {
    const conf = Object.assign({}, this.props.plugins.output.statink);
    conf[flag] = !conf[flag];
    this.dispatch('output:changeStatinkFlag', conf);
  }
}

class ApiKey extends Component {
  constructor(props) {
    super(props);
    this._onChange = this._onChange.bind(this);
  }

  render() {
    return <LabeledInput
        label={t('API Key') + ':'}
        id="output-statink-apikey"
        value={this.props.plugins.output.statink.apikey}
        onChange={this._onChange}
        onFocus={ev => {
          const el = ev.target;
          el.type = "text";
          el.select();
        }}
        onBlur={ev => {
          ev.target.type = "password";
        }}
        type="password"
    />;
  }

  _onChange(e) {
    const value = String(e.target.value).trim();
    this.dispatch('output:changeStatinkApiKey', value);
  }
}

class Anonymizer extends Component {
  constructor(props) {
    super(props);
    this._onToggle = this._onToggle.bind(this);
    this._onChange = this._onChange.bind(this);
  }

  render() {
    return (
      <div>
        <WrappedCheckbox
            name="output-statink-anon-onoff"
            checked={this.props.plugins.output.statink.anonymizer !== false}
            text={t('Enable anonymizer (Hide player names)')}
            onChange={this._onToggle}
          />
        <div className={INDENT}>
          <WrappedRadioButton
              name="output-statink-anon"
              checked={this.props.plugins.output.statink.anonymizer === 'other'}
              text={t('Other players')}
              onChange={() => this._onChange('other')}
            />
          <WrappedRadioButton
              name="output-statink-anon"
              checked={this.props.plugins.output.statink.anonymizer === 'all'}
              text={t('All players')}
              onChange={() => this._onChange('all')}
            />
        </div>
      </div>
    );
  }

  _onToggle() {
    if (this.props.plugins.output.statink.anonymizer === false) {
      this._onChange('other');
    } else {
      this._onChange(false);
    }
  }

  _onChange(newState) {
    this.dispatch('output:changeStatinkAnonymizer', newState);
  }
}
