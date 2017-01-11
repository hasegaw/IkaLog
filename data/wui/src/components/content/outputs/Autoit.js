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
import { LabeledInput, WrappedCheckbox } from '../../elements';

const INDENT = 'offset-1 col-11';
const t = (text) => window.i18n.t(text, {ns: 'output-autoit'});

export default class Autoit extends Component {
  constructor(props) {
    super(props);
    this._onChangeEnable = this._onChangeEnable.bind(this);
    this._onChangeRename = this._onChangeRename.bind(this);
    this._onChangeScriptPath = this._onChangeScriptPath.bind(this);
    this._onChangeOutputPath = this._onChangeOutputPath.bind(this);
  }

  render() {
    const input = this.props.plugins.output.autoit.enabled ? this._renderInput() : null;

    return (
      <fieldset>
        <legend>
          {t('Control video recording app (AutoIt)')}
          <small>
            <a href="https://www.autoitscript.com/site/autoit/" target="_blank">
              <span className="fa fa-fw fa-external-link" />
            </a>
          </small>
        </legend>
        <WrappedCheckbox
            name="output-autoit-enable"
            checked={!!this.props.plugins.output.autoit.enabled}
            text={t('Enable control of video recording applications')}
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
            id="output-autoit-au3"
            label={t('Path to controller scripts (ControlOBS.au3)') + ':'}
            value={this.props.plugins.output.autoit.scriptPath}
            onChange={this._onChangeScriptPath}
        />
        <LabeledInput
            id="output-autoit-outdir"
            label={t('Recordings Folder') + ':'}
            value={this.props.plugins.output.autoit.outputPath}
            onChange={this._onChangeOutputPath}
        />
        <WrappedCheckbox
            name="output-autoit-rename"
            text={t('Automatically rename recorded videos')}
            checked={!!this.props.plugins.output.autoit.rename}
            onChange={this._onChangeRename}
        />
      </div>
    );
  }

  _onChangeEnable() {
    this.dispatch('output:changeAutoitEnable', !this.props.plugins.output.autoit.enabled);
  }

  _onChangeRename() {
    this.dispatch('output:changeAutoitRename', !this.props.plugins.output.autoit.rename);
  }

  _onChangeScriptPath(e) {
    const path = String(e.target.value).trim();
    this.dispatch('output:changeAutoitScriptPath', path);
  }

  _onChangeOutputPath(e) {
    const path = String(e.target.value).trim();
    this.dispatch('output:changeAutoitOutputPath', path);
  }
}
