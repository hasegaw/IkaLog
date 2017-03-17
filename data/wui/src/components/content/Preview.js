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

const t = text => window.i18n.t(text, {ns: 'input'});

export default class Preview extends Component {
  render() {
    return (
      <div>
        <div className="form-group">
          <PreviewImage {...this.props} />
        </div>
        <div className="form-group">
          <div className="btn-group" role="group">
            <CaptureButton {...this.props} />
            <ReloadButton {...this.props} />
          </div>
        </div>
      </div>
    );
  }
}

class PreviewImage extends Component {
  componentDidMount() {
    if (this.props.chrome.preview !== true) {
      if (this.props.chrome.preview !== false) {
        this.dispatch('preview:connect', null);
      } else {
        this.dispatch('preview:reload', null);
      }
    }
  }

  componentWillUnmount() {
    this.dispatch('preview:disconnect', null);
  }

  render() {
    if (this.props.chrome.preview === null) {
      return <Loading {...this.props} />;
    }
    if (this.props.chrome.preview === false) {
      return <FatalError {...this.props} />;
    }

    const style = {
      width: "100%",
      height: "auto",
    };

    return (
      <img src={this.props.chrome.previewStream.src} style={style} />
    );
  }
}

class CaptureButton extends Component {
  constructor(props) {
    super(props);
    this._onClick = this._onClick.bind(this);
  }

  render() {
    const disabled = this.props.tasks.screenshot === 'progress' || !this.props.plugins.output.screenshot.currentEnabled;
    const icon = this.props.tasks.screenshot === 'progress'
      ? 'fa fa-fw fa-circle-o-notch fa-spin'
      : 'fa fa-fw fa-camera'
    return (
      <button
          className="btn btn-secondary"
          disabled={disabled}
          onClick={this._onClick}
      >
        <span className={icon} /> {t('Take a screenshot')}
      </button>
    );
  }

  _onClick() {
    this.dispatch('input:takeScreenshot', 1);
  }
}

class ReloadButton extends Component {
  constructor(props) {
    super(props);
    this._onClick = this._onClick.bind(this);
  }

  render() {
    return (
      <button
          className="btn btn-secondary"
          onClick={this._onClick}
      >
        <span className="fa fa-fw fa-refresh" /> {t('Reload')}
      </button>
    );
  }

  _onClick() {
    this.dispatch('preview:reload', null);
  }
}


class Loading extends Component {
  render() {
    const outerStyle = {
      textAlign: "center",
    };
    return (
      <p style={outerStyle}>
        <span className="fa fa-spinner fa-pulse fa-3x fa-fw"></span>
        <span className="sr-only">Loading...</span>
      </p>
    );
  }
}

class FatalError extends Component {
  render() {
    const outerStyle = {
      textAlign: "center",
    };
    return (
      <p style={outerStyle}>
        <span className="fa fa-frown-o fa-3x fa-fw" style={iconStyle}></span><br />
        <span style={textStyle}>
          Error.
        </span>
      </p>
    );
  }
}
