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
import { WrappedCheckbox, LabeledInput } from '../../../elements';

const INDENT = 'offset-1 col-11';
const t = (text) => window.i18n.t(text, {ns: 'output-speech'});

export default class MMMouth extends Component {
  constructor(props) {
    super(props);
    this._onChangeEnable = this._onChangeEnable.bind(this);
    this._onChangeHost = this._onChangeHost.bind(this);
    this._onChangePort = this._onChangePort.bind(this);
  }

  render() {
    const input = this.props.plugins.output.mikumikumouth.enabled ? this._renderInput() : null;

    return (
      <fieldset>
        <legend>
          {t('MikuMikuMouth')}
          <small>
            <a href="http://mikumikumouth.net/" target="_blank">
              <span className="fa fa-fw fa-external-link" />
            </a>
          </small>
        </legend>
        <WrappedCheckbox
            name="output-mikumikumouth-enable"
            checked={!!this.props.plugins.output.mikumikumouth.enabled}
            text={t('Enable MikuMikuMouth client')}
            onChange={this._onChangeEnable}
        />
        {input}
      </fieldset>
    );
  }

  _renderInput() {
    return (
      <div className={INDENT}>
        <p>
          {t('Please set mode to REST API.')}&#32;
          <a href="http://mikumikumouth.net/developer.html#対応プロトコル" target="_blank">
            <span className="fa fa-fw fa-question" />
          </a>
        </p>
        <LabeledInput
            id="output-mikumikumouth-host"
            label={t('Host') + ':'}
            value={this.props.plugins.output.mikumikumouth.host}
            onChange={this._onChangeHost}
            placeholder={t('Example') + ': 127.0.0.1'}
        />
        <LabeledInput
            id="output-mikumikumouth-port"
            label={t('Port') + ':'}
            type="number"
            value={this.props.plugins.output.mikumikumouth.port}
            onChange={this._onChangePort}
            placeholder={t('Example') + ': 3939'}
        />
      </div>
    );
  }

  _onChangeEnable() {
    this.dispatch('output:changeMikuMikuMouthEnable', !this.props.plugins.output.mikumikumouth.enabled);
  }

  _onChangeHost(e) {
    this.dispatch('output:changeMikuMikuMouthHost', String(e.target.value).trim())
  }

  _onChangePort(e) {
    this.dispatch('output:changeMikuMikuMouthPort', parseInt(String(e.target.value).trim(), 10));
  }
}
