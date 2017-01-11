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
import { RadioButton } from './elements';
import logoImg30 from '../data/logo-30.png';
import logoImg60 from '../data/logo-60.png';
import logoImg90 from '../data/logo-90.png';

export default class Header extends Component {
  render() {
    return (
      <header className="navbar navbar-inverse bg-inverse bd-navbar">
        <div className="container">
          <nav>
            <Brand {...this.props} />
          </nav>
        </div>
      </header>
    );
  }
}

class Brand extends Component {
  render() {
    return (
      <h1 className="navbar-brand mb-0">
        <Logo {...this.props} />
        IkaLog
      </h1>
    );
  }
}

class Logo extends Component {
  constructor(props) {
    super(props);
    this._url = this._decideLogo();
  }

  render() {
    return (
      <img src={this._url} width="30" height="30" className="d-inline-block align-top mr-2" alt="" />
    );
  }

  _decideLogo() {
    const ratio = window ? (window.devicePixelRatio || 1) : 1;
    if (ratio >= 2.25) {
      return logoImg90;
    } else if (ratio >= 1.25) {
      return logoImg60;
    } else {
      return logoImg30;
    }
  }
}
