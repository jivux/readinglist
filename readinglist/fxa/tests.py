import json
from unittest import TestCase

import mock
import responses
from requests import exceptions as requests_exceptions

from readinglist import fxa


class TradeCodeTest(TestCase):
    @responses.activate
    def setUp(self):
        responses.add(responses.POST, 'https://server/token',
            body='{"access_token": "yeah"}',
            content_type='application/json')

        self.token = fxa.trade_code(oauth_uri='https://server',
                                    client_id='abc',
                                    client_secret='cake',
                                    code='1234')

        self.resp_call = responses.calls[0]

    def test_reaches_server_on_token_url(self):
        self.assertEqual(self.resp_call.request.url,
                         'https://server/token')

    def test_posts_code_to_server(self):
        data = json.loads(self.resp_call.request.body)
        expected = {
            "client_secret": "cake",
            "code": "1234",
            "client_id": "abc"
        }
        self.assertDictEqual(data, expected)

    def test_returns_access_token_given_by_server(self):
        self.assertEqual(self.token, "yeah")


class TradeCodeErrorTest(TestCase):
    @mock.patch('readinglist.fxa.requests.post')
    def test_raises_error_if_server_is_unreachable(self, mocked_post):
        mocked_post.side_effect = requests_exceptions.RequestException

        with self.assertRaises(fxa.OAuth2Error):
            fxa.trade_code(oauth_uri='https://unknown',
                           client_id='abc',
                           client_secret='cake',
                           code='1234')

    @responses.activate
    def test_raises_error_if_response_returns_400(self):
        responses.add(responses.POST, 'https://server/token',
            body='{"errorno": "999"}', status=400,
            content_type='application/json')
        with self.assertRaises(fxa.OAuth2Error):
            fxa.trade_code(oauth_uri='https://server',
                           client_id='abc',
                           client_secret='cake',
                           code='1234')

    @responses.activate
    def test_raises_error_if_access_token_not_returned(self):
        responses.add(responses.POST, 'https://server/token',
            body='{"foo": "bar"}',
            content_type='application/json')
        with self.assertRaises(fxa.OAuth2Error):
            fxa.trade_code(oauth_uri='https://server',
                           client_id='abc',
                           client_secret='cake',
                           code='1234')


class VerifyTokenTest(TestCase):
    @responses.activate
    def setUp(self):
        responses.add(responses.POST, 'https://server/verify',
            body='{"user": "alice", "scopes": "profile", "client_id": "abc"}',
            content_type='application/json')

        self.verification = fxa.verify_token(oauth_uri='https://server',
                                             token='abc')

        self.resp_call = responses.calls[0]

    def test_reaches_server_on_verify_url(self):
        self.assertEqual(self.resp_call.request.url,
                         'https://server/verify')

    def test_posts_token_to_server(self):
        data = json.loads(self.resp_call.request.body)
        expected = {
            "token": "abc",
        }
        self.assertDictEqual(data, expected)

    def test_returns_response_given_by_server(self):
        expected = {
            "user": "alice",
            "scopes": "profile",
            "client_id": "abc"
        }
        self.assertDictEqual(self.verification, expected)


class VerifyTokenErrorTest(TestCase):
    @mock.patch('readinglist.fxa.requests.post')
    def test_raises_error_if_server_is_unreachable(self, mocked_post):
        mocked_post.side_effect = requests_exceptions.RequestException

        with self.assertRaises(fxa.OAuth2Error):
            fxa.verify_token(oauth_uri='https://unknown',
                             token='1234')

    @responses.activate
    def test_raises_error_if_response_returns_400(self):
        responses.add(responses.POST, 'https://server/verify',
            body='{"errorno": "999"}', status=400,
            content_type='application/json')
        with self.assertRaises(fxa.OAuth2Error):
            fxa.verify_token(oauth_uri='https://server',
                             token='1234')

    @responses.activate
    def test_raises_error_if_some_attributes_are_not_returned(self):
        responses.add(responses.POST, 'https://server/verify',
            body='{"foo": "bar"}',
            content_type='application/json')
        with self.assertRaises(fxa.OAuth2Error):
            fxa.verify_token(oauth_uri='https://server',
                             token='1234')
