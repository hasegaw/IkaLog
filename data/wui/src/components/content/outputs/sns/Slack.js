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
const t = (text) => window.i18n.t(text, {ns: 'output-sns'});

export default class Slack extends Component {
  constructor(props) {
    super(props);
    this._onChangeEnable = this._onChangeEnable.bind(this);
    this._onChangeUrl = this._onChangeUrl.bind(this);
    this._onChangeBotName = this._onChangeBotName.bind(this);
  }

  render() {
    const input = this.props.plugins.output.slack.enabled ? this._renderInput() : null;

    return (
      <fieldset>
        <legend>
          <span className="fa fa-slack fa-fw" />
          {t('Slack')}
          <small>
            <a href="https://slack.com/" target="_blank">
              <span className="fa fa-external-link fa-fw" />
            </a>
          </small>
        </legend>
        <WrappedCheckbox
            name="output-slack-enable"
            checked={!!this.props.plugins.output.slack.enabled}
            text={t('Post game results to a Slack channel')}
            onChange={this._onChangeEnable}
        />
        {input}
      </fieldset>
    );
  }

  _renderInput() {
    const webhookLabel = (
      <span>
        {t('Incoming WebHook API URL') + ':'}
        <a href="https://my.slack.com/services/new/incoming-webhook/" target="_blank">
          <span className="fa fa-fw fa-external-link" />
        </a>
      </span>
    );
    return (
      <div className={INDENT}>
        <LabeledInput
            id="output-slack-url"
            label={webhookLabel}
            value={this.props.plugins.output.slack.webhook}
            onChange={this._onChangeUrl}
            placeholder="https://hooks.slack.com/services/AAAAAAAAA/BBBBBBBBB/CCCCCCCCCCCCCCCCCCCCCCCC"
        />
        <LabeledInput
            id="output-slack-name"
            label={t('Bot name') + ':'}
            value={this.props.plugins.output.slack.botName}
            onChange={this._onChangeBotName}
        />
      </div>
    );
  }

  _onChangeEnable() {
    this.dispatch('output:changeSlackEnable', !this.props.plugins.output.slack.enabled);
  }

  _onChangeUrl(e) {
    this.dispatch('output:changeSlackUrl', String(e.target.value).trim())
  }

  _onChangeBotName(e) {
    this.dispatch('output:changeSlackBotName', String(e.target.value).trim())
  }
}
