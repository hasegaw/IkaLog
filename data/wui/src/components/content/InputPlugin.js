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
import { WrappedRadioButton, WrappedCheckbox, LabeledInput } from '../elements';

const RADIO_NAME = 'radio-9964c174-5d60-485a-b75d-ec15c80609f8';
const INDENT = 'offset-1 col-11';

const t = text => window.i18n.t(text, {ns: 'input'});

export default class InputPlugin extends Component {
  render() {
    return (
      <div className="card">
        <h1 className="card-header">
          {t('Video Input')}
        </h1>
        <div className="card-block">
          <fieldset>
            <legend>
              {t('Select input source')}
            </legend>
            <Amarec {...this.props} />
            <DirectShow {...this.props} />
            <AVFoundationCapture {...this.props} />
            <OpenCV {...this.props} />
            {/* <Capture {...this.props} /> */}
            {/* <File {...this.props} /> */}
          </fieldset>
        </div>
      </div>
    );
  }
}

class Amarec extends Component {
  constructor(props) {
    super(props);
    this._onChange = this._onChange.bind(this);
  }

  render() {
    if (!this.props.system.isWindows) {
      return null;
    }
    const dshow = this.props.plugins.input.classes.DirectShow;
    const enabled = dshow && dshow.length > 0 && (() => {
      let ret = false;
      dshow.forEach(val => {
        if (val.source === 'AmaRec Video Capture') {
          ret = true;
        }
      });
      return ret;
    })();

    return (
      <WrappedRadioButton
          name={RADIO_NAME}
          checked={this.props.plugins.input.driver === 'amarec'}
          onChange={this._onChange}
          text={t('Capture through AmarecTV')}
          disabled={!enabled}
      />
    );
  }

  _onChange() {
    this.dispatch('input:changeSource', 'amarec');
  }
}

class DirectShow extends Component {
  constructor(props) {
    super(props);
    this._onChange = this._onChange.bind(this);
  }

  render() {
    if (!this.props.system.isWindows) {
      return null;
    }
    const root = this.props.plugins.input.classes.DirectShow;
    const enabled = root && root.length > 0;
    const devices = enabled ? root : [];

    return (
      <div>
        <WrappedRadioButton
            name={RADIO_NAME}
            checked={this.props.plugins.input.driver === 'directshow'}
            onChange={this._onChange}
            text={t('HDMI video input (DirectShow, recommended)')}
            disabled={!enabled}
        />
        <DeviceList driver="directshow" devices={devices} {...this.props} />
      </div>
    );
  }

  _onChange() {
    this.dispatch('input:changeSource', 'directshow');
  }
}

class AVFoundationCapture extends Component {
  constructor(props) {
    super(props);
    this._onChange = this._onChange.bind(this);
  }

  render() {
    if (!this.props.system.isMacOS) {
      return null;
    }
    const root = this.props.plugins.input.classes.AVFoundationCapture;
    const enabled = root && root.length > 0;
    const devices = enabled ? root : [];

    return (
      <div>
        <WrappedRadioButton
            name={RADIO_NAME}
            checked={this.props.plugins.input.driver === 'avfoundation'}
            onChange={this._onChange}
            text={t('HDMI video input (AVFoundation, recommended)')}
            disabled={!enabled}
        />
        <DeviceList driver="avfoundation" devices={devices} {...this.props} />
      </div>
    );
  }

  _onChange() {
    this.dispatch('input:changeSource', 'avfoundation');
  }
}

class OpenCV extends Component {
  constructor(props) {
    super(props);
    this._onChange = this._onChange.bind(this);
  }

  render() {
    const root = this.props.plugins.input.classes.CVCapture;
    const enabled = root && root.length > 0;
    const devices = enabled ? root : [];

    return (
      <div>
        <WrappedRadioButton
            name={RADIO_NAME}
            checked={this.props.plugins.input.driver === 'opencv'}
            onChange={this._onChange}
            text={t('HDMI video input (OpenCV driver)')}
            disabled={!enabled}
        />
        <DeviceList driver="opencv" devices={devices} {...this.props} />
      </div>
    );
  }

  _onChange() {
    this.dispatch('input:changeSource', 'opencv');
  }
}

// class Capture extends Component {
//   constructor(props) {
//     super(props);
//     this._onChange = this._onChange.bind(this);
//   }
// 
//   render() {
//     return (
//       <div>
//         <WrappedRadioButton
//             name={RADIO_NAME}
//             checked={this.props.plugins.input.driver === 'capture'}
//             onChange={this._onChange}
//             text={t('Realtime capture from desktop')}
//         />
//         <CalibrateButtons {...this.props} />
//       </div>
//     );
//   }
// 
//   _onChange() {
//     this.dispatch('input:changeSource', 'capture');
//   }
// }
// 
// class CalibrateButtons extends Component {
//   constructor(props) {
//     super(props);
//     this._calibrate = this._calibrate.bind(this);
//     this._reset = this._reset.bind(this);
//   }
// 
//   render() {
//     if (this.props.plugins.input.driver !== 'capture') {
//       return null;
//     }
//     return (
//       <div className={INDENT + ' form-group'}>
//         <div className="btn-group">
//           <button type="button" className="btn btn-secondary" onChange={this._calibrate}>
//             <span className="fa fa-search fa-fw" />
//             {t('Calibrate')}
//           </button>
//           <button type="button" className="btn btn-secondary" onChange={this._reset}>
//             <span className="fa fa-undo fa-fw" />
//             {t('Reset')}
//           </button>
//         </div>
//       </div>
//     );
//   }
// 
//   _calibrate() {
//     this.dispatch('input:calibrate', true);
//   }
// 
//   _reset() {
//     this.dispatch('input:calibrate', false);
//   }
// }
// 
// class File extends Component {
//   constructor(props) {
//     super(props);
//     this._onChange = this._onChange.bind(this);
//   }
// 
//   render() {
//     return (
//       <div>
//         <WrappedRadioButton
//             name={RADIO_NAME}
//             checked={this.props.plugins.input.driver === 'file'}
//             onChange={this._onChange}
//             text={t('Read from pre-recorded video file (for testing)')}
//         />
//         <FileSettings {...this.props} />
//       </div>
//     );
//   }
// 
//   _onChange() {
//     this.dispatch('input:changeSource', 'file');
//   }
// }
// 
// class FileSettings extends Component {
//   constructor(props) {
//     super(props);
//     this._onChangeFilename = this._onChangeFilename.bind(this);
//     this._onChangeDeinterlace = this._onChangeDeinterlace.bind(this);
//   }
// 
//   render() {
//     if (this.props.plugins.input.driver !== 'file') {
//       return null;
//     }
//     return (
//       <div className={INDENT}>
//         <LabeledInput
//             id="input-file-name"
//             label={t('Video file path') + ':'}
//             value={this.props.plugins.input.filePath}
//             onChange={this._onChangeFilename}
//         />
//         <WrappedCheckbox
//             checked={this.props.plugins.input.fileDeinterlace}
//             onChange={this._onChangeDeinterlace}
//             text={t('Enable deinterlacing (experimental)')}
//         />
//       </div>
//     );
//   }
// 
//   _onChangeDeinterlace() {
//     this.dispatch('input:changeFileDeinterlace', !this.props.plugins.input.fileDeinterlace);
//   }
// 
//   _onChangeFilename(e) {
//     this.dispatch('input:changeFileName', String(e.target.value).trim());
//   }
// }

class DeviceList extends Component {
  constructor(props) {
    super(props);
    this._onChange = this._onChange.bind(this);
  }

  render() {
    if (this.props.plugins.input.driver !== this.props.driver) {
      return null;
    }
    const devices = this.props.devices;
    return (
      <div className={INDENT}>
        <div className="form-group">
          <select
              id="device"
              className="form-control mb-1"
              size="10"
              defaultValue={JSON.stringify(this.props.plugins.input.device)}
              onChange={this._onChange}
          >
            {devices.map(device => <option value={JSON.stringify(device)}>{device.source}</option>)}
          </select>
        </div>
      </div>
    );
  }

  _onChange(e) {
    this.dispatch('input:changeDevice', JSON.parse(e.target.value));
  }
}
