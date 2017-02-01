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
import { stopEvent } from '../../Utils';
import File from './outputs/File';
// import Sns from './outputs/Sns';
import Statink from './outputs/Statink';
import Speech from './outputs/Speech';
// import Autoit from './outputs/Autoit';
// import WebSocket from './outputs/WebSocket';

const t = (text, ns) => window.i18n.t(text, {ns: ns});

export default class OutputPlugin extends Component {
  render() {
    const content = (tab => {
      switch (tab) {
        case 'file':
          return <File {...this.props} />;

        // case 'sns':
        //   return <Sns {...this.props} />;

        case 'statink':
          return <Statink {...this.props} />;

        case 'speech':
          return <Speech {...this.props} />;

        //case 'autoit':
        //  return <Autoit {...this.props} />;

        //case 'websocket':
        //  return <WebSocket {...this.props} />;

        default:
          return <div>Not impl.: {tab} </div>;
      }
    })(this.props.chrome.pluginTab);

    return (
      <div className="card">
        <div className="card-header">
          <ul className="nav nav-tabs card-header-tabs float-xs-left">
            <NavItem text='File'       target='file'      {...this.props} />
            {/* <NavItem text='SNS'        target='sns'       {...this.props} /> */}
            <NavItem text='stat.ink'   target='statink'   {...this.props} />
            <NavItem text='Speech App' target='speech'    {...this.props} />
            {/* <NavItem text='Recording'  target='autoit'    {...this.props} /> */}
            {/* <NavItem text='WebSocket'  target='websocket' {...this.props} /> */}
          </ul>
        </div>
        <div className="card-block">
          {content}
        </div>
      </div>
    );
  }
}

class NavItem extends Component {
  constructor(props) {
    super(props);
    this._onClick = this._onClick.bind(this);
  }

  render() {
    const selected = this.props.target === this.props.chrome.pluginTab;
    const classes = 'nav-link' + (selected ? ' active' : '');
    return (
      <li className="nav-item">
        <a className={classes} href="#" onClick={this._onClick}>
          {t(this.props.text, 'app')}
        </a>
      </li>
    );
  }

  _onClick(e) {
    this.dispatch('chrome:changePluginTab', this.props.target);
    stopEvent(e);
  }
}
