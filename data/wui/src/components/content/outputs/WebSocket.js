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
import { WrappedCheckbox, LabeledInput } from '../../elements';

const INDENT = 'offset-1 col-11';
const t = (text) => window.i18n.t(text, {ns: 'output-websocket'});

export default class WebSocket extends Component {
  constructor(props) {
    super(props);
    this._onChangeEnable = this._onChangeEnable.bind(this);
    this._onChangePort = this._onChangePort.bind(this);
  }

  render() {
    const input = this.props.plugins.output.websocket.enabled ? this._renderInput() : null;

    return (
      <fieldset>
        <legend>
          {t('WebSocket Server')}
        </legend>
        <p className="alert alert-warning">
          <strong>{t('Warning')}:</strong> {t('The server is accessible by anyone')}
        </p>
        <WrappedCheckbox
            name="output-websocket-enable"
            checked={!!this.props.plugins.output.websocket.enabled}
            text={t('Enable WebSocket server')}
            onChange={this._onChangeEnable}
        />
        {input}
      </fieldset>
    );
  }

  _renderInput() {
    return (
      <div className={INDENT}>
        <LabeledInput
            id="output-websocket-port"
            label={t('Port') + ':'}
            type="number"
            value={this.props.plugins.output.websocket.port}
            onChange={this._onChangePort}
            placeholder={t('Example') + ': 9090'}
            min="1"
            max="65535"
        />
      </div>
    );
  }

  _onChangeEnable() {
    this.dispatch('output:changeWebSocketEnable', !this.props.plugins.output.websocket.enabled);
  }

  _onChangePort(e) {
    this.dispatch('output:changeWebSocketPort', parseInt(String(e.target.value).trim(), 10));
  }
}
