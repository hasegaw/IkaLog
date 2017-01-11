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

export default class Screenshot extends Component {
  constructor(props) {
    super(props);
    this._onChangeEnable = this._onChangeEnable.bind(this);
    this._onChangePath = this._onChangePath.bind(this);
  }

  render() {
    const input = this.props.plugins.output.screenshot.enabled ? this._renderInput() : null;

    return (
      <fieldset>
        <legend>
          <span className="fa fa-file-image-o fa-fw" />
          {t('Screenshot')}
        </legend>
        <WrappedCheckbox
            name="output-screenshot-enable"
            checked={!!this.props.plugins.output.screenshot.enabled}
            text={t('Save screenshots of game results')}
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
            id="output-screenshot-filepath"
            label={t('Folder to save screenshots') + ':'}
            value={this.props.plugins.output.screenshot.path}
            onChange={this._onChangePath}
        />
      </div>
    );
  }

  _onChangeEnable() {
    this.dispatch('output:changeScreenshotEnable', !this.props.plugins.output.screenshot.enabled);
  }

  _onChangePath(e) {
    this.dispatch('output:changeScreenshotPath', String(e.target.value).trim())
  }
}
