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
const t = (text) => window.i18n.t(text, {ns: 'output-file'});

export default class Json extends Component {
  constructor(props) {
    super(props);
    this._onChangeEnable = this._onChangeEnable.bind(this);
    this._onChangePath = this._onChangePath.bind(this);
  }

  render() {
    const input = this.props.plugins.output.json.enabled ? this._renderInput() : null;

    return (
      <fieldset>
        <legend>
          <span className="fa fa-file-code-o fa-fw"></span>
          {t('JSON output')}
        </legend>
        <WrappedCheckbox
            name="output-json-enable"
            checked={!!this.props.plugins.output.json.enabled}
            text={t('Enable JSON Log')}
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
            id="output-json-filepath"
            label={t('Log filename') + ':'}
            value={this.props.plugins.output.json.path}
            onChange={this._onChangePath}
        />
      </div>
    );
  }

  _onChangeEnable() {
    this.dispatch('output:changeJsonEnable', !this.props.plugins.output.json.enabled);
  }

  _onChangePath(e) {
    this.dispatch('output:changeJsonPath', String(e.target.value).trim())
  }
}
