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

import React, { Component } from 'react';
import { stopEvent } from '../Utils';
import Sidebar from './Sidebar';
import MainContent from './MainContent';

export default class Content extends Component {
  render() {
    const classesMain = this._addPushClass([
      'col-12',
      'col-sm-7',
      'col-md-8',
      'col-lg-9',
      'col-xl-9',
    ]);
    const classesSide = this._addPullClass(this._makeCounterSide(classesMain));

    return (
      <div className="container mt-2">
        <div className="row">
          <XsHelper {...this.props} />
          <MainContent className={classesMain.join(' ')} {...this.props} />
          <Sidebar className={classesSide.join(' ')} {...this.props} />
        </div>
      </div>
    );
  }

  // 左右入れ替えのための push-**-** クラスを生成して返す (col-md-10 => col-md-10 push-md-2)
  _addPushClass(classes) {
    return this._addPushPullClass(classes, 'push');
  }

  // 左右入れ替えのための pull-**-** クラスを生成して返す (col-md-10 => col-md-10 pull-md-2)
  _addPullClass(classes) {
    return this._addPushPullClass(classes, 'pull');
  }

  // _addPushClass/_addPullClass の実装関数
  _addPushPullClass(classes, pushOrPull) {
    const ret = [];
    classes.forEach(className => {
      const match = className.match(/^col-([a-z]{2})-(\d+)$/);
      ret.push(className);
      if (!match || match[2] === '12') {
        return;
      }
      const push = 12 - parseInt(match[2], 10);
      ret.push(`${pushOrPull}-${match[1]}-${push}`);
    });
    return ret;
  }

  // 2カラムレイアウトの反対側のクラスを自動生成する(col-**-** の合計が12になるように作る)
  _makeCounterSide(classes) {
    const ret = [];
    classes.forEach(className => {
      const match = className.match(/^col-(?:([a-z]{2})-)?(\d+)$/);
      if (!match) {
        return;
      }
      if (match[2] === '12') {
        ret.push(className);
        return;
      }
      const width = 12 - parseInt(match[2], 10);
      ret.push(`col-${match[1]}-${width}`);
    });
    return ret;
  }
}

class XsHelper extends Component {
  constructor(props) {
    super(props);
    this._onClick = this._onClick.bind(this);
  }

  render() {
    return (
      <div className="col-12 hidden-sm-up">
        <div className="text-right text-xs-right mb-2">
          <button className="btn btn-secondary" onClick={this._onClick}>
            <span className="fa fa-fw fa-angle-double-down" />
            {window.i18n.t('Menu', {ns: 'sidebar'})}
          </button>
        </div>
      </div>
    );
  }

  _onClick(e) {
    const $ = window.jQuery;
    const $target = $('#menu');
    $('body,html').animate({scrollTop:$target.offset().top - 16}, 'fast');
    $('body,html').animate({scrollLeft:0}, 'fast');
    stopEvent(e);
  }
}
