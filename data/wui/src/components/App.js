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
import Header from './Header';
import Content from './Content';
import NotificationSystem from 'react-notification-system';
import favicon from '../data/logo-16.png';

export default class App extends Component {
  componentDidMount() {
    this._kickInitEvent();
    this._setFavicon();
  }

  _setFavicon() {
    if (this.props.chrome.favicon) {
      return;
    }
    
    document.head.appendChild(
      (() => {
        const link = document.createElement('link');
        link.rel = 'icon';
        link.type = 'image/png';
        link.href = favicon;
        return link;
      })()
    );

    this.dispatch('chrome:favicon', true);
  }

  _kickInitEvent() {
    this.dispatch(':init');
  }

  render() {
    if (this.props.chrome.fatalError) {
      return <FatalError {...this.props} />
    }
    if (!this.props.system || !this.props.plugins) {
      return <Loading {...this.props} />
    }
    return <AppMain {...this.props} />
  }
}

class AppMain extends Component {
  componentDidMount() {
    window.notifications = this.refs.notificationSystem;
  }

  componentWillUnmount() {
    window.notifications = undefined;
  }

  render() {
    return (
      <div>
        <Header {...this.props} />
        <Content {...this.props} />
        <LockScreen {...this.props} />
        <NotificationSystem ref="notificationSystem" />
      </div>
    );
  }
}

class Loading extends Component {
  render() {
    const outerStyle = {
      display: "flex",
      justifyContent: "center",
      alignItems: "center",
      height: "100%",
    };
    const innerStyle = {
      fontSize: "150px",
    };
    return (
      <div style={outerStyle}>
        <p>
          <span className="fa fa-spinner fa-pulse fa-fw" style={innerStyle}></span>
          <span className="sr-only">Loading...</span>
        </p>
      </div>
    );
  }
}

class FatalError extends Component {
  render() {
    const outerStyle = {
      display: "flex",
      justifyContent: "center",
      alignItems: "center",
      height: "100%",
      textAlign: "center",
    };
    const iconStyle = {
      fontSize: "150px",
    };
    const textStyle = {
      fontSize: "30px",
    };
    return (
      <div style={outerStyle}>
        <p>
          <span className="fa fa-frown-o fa-fw" style={iconStyle}></span><br />
          <span style={textStyle}>
            Error.
          </span>
        </p>
      </div>
    );
  }
}

class LockScreen extends Component {
  render() {
    if (!this.props.chrome.lock) {
      return null;
    }
    const outerStyle = {
      display: "flex",
      justifyContent: "center",
      alignItems: "center",
      height: "100%",
      width: "100%",
      position: "absolute",
      left: 0,
      top: 0,
      zIndex: 65535,
      backgroundColor: "rgba(0,0,0,.85)",
    };
    const innerStyle = {
      fontSize: "150px",
      color: "rgba(255,255,255,.5)",
    };
    return (
      <div style={outerStyle}>
        <p>
          <span className="fa fa-circle-o-notch fa-spin fa-fw" style={innerStyle}></span>
          <span className="sr-only">Loading...</span>
        </p>
      </div>
    );
  }
}
