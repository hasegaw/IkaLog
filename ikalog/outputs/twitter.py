#!/usr/bin/env python3
# -*- coding: utf-8 -*-
#
#  IkaLog
#  ======
#  Copyright (C) 2017 Takeshi HASEGAWA
#
#  Licensed under the Apache License, Version 2.0 (the "License");
#  you may not use this file except in compliance with the License.
#  You may obtain a copy of the License at
#
#      http://www.apache.org/licenses/LICENSE-2.0
#
#  Unless required by applicable law or agreed to in writing, software
#  distributed under the License is distributed on an "AS IS" BASIS,
#  WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
#  See the License for the specific language governing permissions and
#  limitations under the License.
#

import os
import json

import cv2
from requests_oauthlib import OAuth1Session

from ikalog.plugin import IkaLogPlugin
from ikalog.utils import *

oauth_endpoint = 'https://api.twitter.com/oauth/'
request_token_url = '%s/request_token' % oauth_endpoint 
authorization_url = '%s/authorize' % oauth_endpoint
access_token_url = '%s/access_token' % oauth_endpoint

_ = Localization.gettext_translation('twitter', fallback=True).gettext

def _get_cert_path(self):
    return Certifi.where() or False


class TwitterPlugin(IkaLogPlugin):

    # TODO
    _preset_ck = None
    _preset_cs = None

    # API Endpoint for Tweets
    url = "https://api.twitter.com/1.1/statuses/update.json"
    # API Endpoint for Medias (screenshots)
    url_media = "https://upload.twitter.com/1.1/media/upload.json"

    def __init__(self):
        super(TwitterPlugin, self).__init__()
        self._img_scoreboard = None

    def on_initialize_plugin(self, context):
        engine = context['engine']['engine']
        engine.set_service('twitter_post', self.tweet)
        engine.set_service('twitter_post_media', self.post_media)
        engine.set_service('twitter_has_preset_key', self._has_preset_key)
        engine.set_service('twitter_oauth1', self._has_preset_key)

    def on_reset_configuration(self, config):
        config = self.config
        config['enabled'] = False
        config['attach_image'] = False
        config['tweet_kd'] = False
        config['tweet_my_score'] = False
        config['tweet_udemae'] = False
        config['use_reply'] = True
        config['consumer_key_type'] = 'ikalog'
        config['consumer_key'] = ''
        config['consumer_secret'] = ''
        config['access_token'] = ''
        config['access_token_secret'] = ''
        config['footer'] = ''

    def on_validate_configuration(self, config):
        pass


    def on_set_configuration(self, config):
        self.config['dest_dir'] = config['dest_dir']
        self.config['enabled'] = config['enabled']

    def _has_preset_key(self):
        return (self._preset_ck is not None) and (self._preset_cs is not None)

    def on_oauth_first(self):
        """
        Start OAuth process. 
        """

        oauth_session = OAuth1Session(
            self._preset_ck, client_secret=self._preset_cs, callback_uri='oob')
        step1 = oauth_session.fetch_request_token(
            request_token_url, verify=_get_cert_path()
        )
        auth_web_url = oauth_session.authorization_url(
            authorization_url, verify=_get_cert_path()
        )
        self._last_oauth_session = oauth_session
        self._last_step1 = step1
        return auth_web_url

    def on_oauth_second(self, pin):
        """
        Comlete OAuth process.
        """

        # FIXME: check age of self._step1
        oauth_session = self._last_oauth_session
        step1 = self._last_step1

        oauth_session.params['oauth_verifier'] = pin
        r = oauth_session.get(
            '%s?oauth_token=%s' %(access_token_url, step1['oauth_token']),
            verify=_get_cert_path()
        )

        d = oauth_session.parse_authorization_response('?' + r.text)

        AT = d.get('oauth_token')
        ATS = d.get('oauth_token_secret')

        if (AT is None) or (ATS) is None:
            # error
            return False

        updated_config = {
            'access_token': AT,
            'access_token_secret': ATS,
            'consumer_key_type': 'ikalog',
            'authenticated_screen_name': d.get('screen_name', (Null))
        }
        self.on_set_configuration(updated_config)
        return True


    def tweet(self, s, media=None):
        params = {'status': s}
        if media is not None:
            params['media_ids'] = [media]

        CK = self._preset_ck if self.consumer_key_type == 'ikalog' else self.consumer_key
        CS = self._preset_cs if self.consumer_key_type == 'ikalog' else self.consumer_secret

        twitter = OAuth1Session(
            CK, CS, self.access_token, self.access_token_secret)
        return twitter.post(self.url, params=params, verify=_get_cert_path())


    def post_media(self, img):
        result, img_png = cv2.imencode('.png', img)

        if not result:
            IkaUtils.dprint('%s: Failed to encode the image (%s)' %
                            (self, img.shape))
            return None

        files = { "media": img_png.tostring() }

        CK = self._preset_ck if self.consumer_key_type == 'ikalog' else self.consumer_key
        CS = self._preset_cs if self.consumer_key_type == 'ikalog' else self.consumer_secret

        twitter = OAuth1Session(
            CK, CS, self.access_token, self.access_token_secret
        )
        req = twitter.post(
            self.url_media,
            files=files,
            verify=self._get_cert_path()
        )

        if req.status_code == 200:
            return json.loads(req.text)['media_id']

        IkaUtis.dprint('%s: Failed to post media.' % self)
        return None

    ##
    # get_text_game_individual_result
    # Generate a record for on_game_individual_result.
    # @param self      The Object Pointer.
    # @param context   IkaLog context
    #
    def get_text_game_individual_result(self, context):
        stage = IkaUtils.map2text(context['game']['map'], unknown=_('unknown stage'))
        rule = IkaUtils.rule2text(context['game']['rule'], unknown=_('unknown rule'))

        result = IkaUtils.getWinLoseText(
            context['game']['won'], win_text=_('won'),
            lose_text=_('lost'),
            unknown_text=_('played'))

        t = IkaUtils.get_end_time(context).strftime("%Y/%m/%d %H:%M")

        s = _('Just %(result)s %(rule)s at %(stage)s') % \
            { 'stage': stage, 'rule': rule, 'result': result}

        me = IkaUtils.getMyEntryFromContext(context)

        if ('score' in me) and self.tweet_my_score:
            s = s + ' %sp' % (me['score'])

        if ('kills' in me) and ('deaths' in me) and self.tweet_kd:
            s = s + ' %dk/%dd' % (me['kills'], me['deaths'])

        if ('udemae_pre' in me) and self.tweet_udemae:
            s = s + _(' Rank: %s') % (me['udemae_pre'])

        fes_title = IkaUtils.playerTitle(me)
        if fes_title:
            s = s + ' %s' % (fes_title)

        s = s + ' (%s) %s #IkaLogResult' % (t, self.footer)

        if self.use_reply:
            s = '@_ikalog_ ' + s

        return s

    def on_result_detail_still(self, context):
        self._img_scoreboard = context['game']['image_scoreboard']

    def on_game_session_end(self, context):
        if not self.config['enabled']:
            return False

        if self._img_scoreboard is None:
            return False

        s = self.get_text_game_individual_result(context)
        IkaUtils.dprint('Tweet: %s' % s)

        media = None
        if self.config['attach_image']:
            media = self.post_media(self._img_scoreboard)

        response = self.tweet(s, media=media)
        if response.status_code != 200:
            IkaUtils.dprint('%s: Tweeting failed. Status code = %d' % (self, response.status_code))

        self._img_scoreboard = None


class Twitter(object):
    pass
