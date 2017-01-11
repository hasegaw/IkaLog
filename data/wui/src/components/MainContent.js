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
import Preview from './content/Preview';
import InputPlugin from './content/InputPlugin';
import OutputPlugin from './content/OutputPlugin';

export default class MainContent extends Component {
  render() {
    const content = (() => {
      switch (this.props.chrome.content) {
        case 'preview':
          return <Preview {...this.props} />;
        case 'input':
          return <InputPlugin {...this.props} />;
        case 'output':
          return <OutputPlugin {...this.props} />;
        default:
          return <p>Error</p>;
      }
    })();
    return (
      <div className={this.props.className} id="main">
        {content}
      </div>
    );
  }
}
