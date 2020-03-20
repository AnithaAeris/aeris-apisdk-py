# Copyright 2020 Aeris Communications Inc.
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     https://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.

import copy
import json
import unittest

from unittest.mock import Mock

import aerisapisdk.aerisconfig as aerisconfig
import aerisapisdk.aerframesdk as aerframesdk
from aerisapisdk.exceptions import ApiException

import responses

from tests.AerTestCase import AerTestCase

# AerAdmin URL for testing -- pretend that aerisconfig always points to this URL
TEST_AF_URL = 'https://localhost'
TEST_LP_URL = 'https://localhost_longpoll.local'
aerisconfig.get_aerframe_api_url = Mock(return_value=TEST_AF_URL)
aerisconfig.get_aerframe_longpoll_url = Mock(return_value=TEST_LP_URL)

EMPTY_RESPONSE_BODY = ''


class TestAerFrameSDK(AerTestCase):
    accountId = '123'
    apiKey = 'anApiKey'
    email = 'foo@bar.com'
    deviceIdType = 'IMSI'
    deviceId = '123456789012345'
    verbose = False

    def test_get_application_endpoint_without_application_id(self):
        result = aerframesdk.get_application_endpoint(self.accountId, None)
        self.assertEqual(TEST_AF_URL + '/registration/v2/' + self.accountId + '/applications', result)

    def test_get_application_endpoint_with_application_id(self):
        result = aerframesdk.get_application_endpoint(self.accountId, '42')
        self.assertEqual(TEST_AF_URL + '/registration/v2/' + self.accountId + '/applications/42', result)

    def test_get_channel_endpoint_without_channel_id(self):
        result = aerframesdk.get_channel_endpoint(self.accountId, None)
        self.assertEqual(TEST_AF_URL + '/notificationchannel/v2/' + self.accountId + '/channels', result)

    def test_get_channel_endpoint_with_channel_id(self):
        result = aerframesdk.get_channel_endpoint(self.accountId, '99')
        self.assertEqual(TEST_AF_URL + '/notificationchannel/v2/' + self.accountId + '/channels/99', result)

    @responses.activate
    def test_get_applications_happy_path(self):
        shortNameToSearch = 'the-one-that-should-be-found'
        expectedApplicationId = '44444444-2943-1346-6c49-123456789abc'
        response_json = {
            "application": [
                {
                    "applicationName": "SMSAPP",
                    "applicationShortName": shortNameToSearch,
                    "applicationTag": "aerframe",
                    "description": "AerFrame application",
                    "apiKey": "12345678-1f85-11e9-adfb-123456789abc",
                    "resourceURL": TEST_AF_URL + "/registration/v2/123/applications/"
                                   + expectedApplicationId,
                    "useSmppInterface": False
                },
                {
                    "applicationName": "SMSAPP",
                    "applicationShortName": "another-short-name",
                    "applicationTag": "aerframe_but_different",
                    "description": "AerFrame application",
                    "apiKey": "87654321-34f2-11e9-8cde-cba987654321",
                    "resourceURL": TEST_AF_URL + "/registration/v2/123/"
                                   + "applications/10101010-d418-2dea-66f2-feedcafefeed",
                    "useSmppInterface": False
                }
            ],
            "resourceURL": TEST_AF_URL + "/registration/v2/123/applications"
        }

        callback = self.create_body_assertion(None, {'apiKey': self.apiKey}, response_json)
        responses.add_callback(responses.GET,
                               TEST_AF_URL + '/registration/v2/' + self.accountId + '/applications',
                               callback=callback
                               )

        result = aerframesdk.get_applications(self.accountId, self.apiKey, shortNameToSearch, self.verbose)
        self.assertEqual(expectedApplicationId, result)

    @responses.activate
    def test_get_applications_short_name_not_found(self):
        short_name_to_search = 'the-one-that-should-be-found'
        expected_application_id = None
        response_json = {
            "application": [
                {
                    "applicationName": "SMSAPP",
                    "applicationShortName": short_name_to_search + 'some-extra-data-to-make-it-not-found',
                    "applicationTag": "aerframe",
                    "description": "AerFrame application",
                    "apiKey": "12345678-1f85-11e9-adfb-123456789abc",
                    "resourceURL": TEST_AF_URL + "/registration/v2/123/"
                                   + "applications/44444444-2943-1346-6c49-123456789abc",
                    "useSmppInterface": False
                },
                {
                    "applicationName": "SMSAPP",
                    "applicationShortName": "another-short-name",
                    "applicationTag": "aerframe_but_different",
                    "description": "AerFrame application",
                    "apiKey": "87654321-34f2-11e9-8cde-cba987654321",
                    "resourceURL": TEST_AF_URL + "/registration/v2/123/"
                                   + "applications/10101010-d418-2dea-66f2-feedcafefeed",
                    "useSmppInterface": False
                }
            ],
            "resourceURL": TEST_AF_URL + "/registration/v2/123/applications"
        }

        callback = self.create_body_assertion(None, {'apiKey': self.apiKey}, response_json)
        responses.add_callback(responses.GET,
                               TEST_AF_URL + '/registration/v2/' + self.accountId + '/applications',
                               callback=callback
                               )

        result = aerframesdk.get_applications(self.accountId, self.apiKey, short_name_to_search, self.verbose)
        self.assertEqual(expected_application_id, result)

    @responses.activate
    def test_get_applications_http_401(self):
        short_name_to_search = 'the-one-that-should-be-found'
        expected_response_headers = {'Content-Length': '0'}

        callback = self.create_empty_request_empty_response_assertion(401, expected_response_headers)
        responses.add_callback(responses.GET,
                               TEST_AF_URL + '/registration/v2/' + self.accountId + '/applications',
                               callback=callback
                               )

        with self.assertRaises(ApiException) as context:
            aerframesdk.get_applications(self.accountId, self.apiKey, short_name_to_search, self.verbose)
        # the requests - or responses - library likes adding a Content-Type header for an empty response body
        self.verify_api_exception(context.exception, 401, EMPTY_RESPONSE_BODY,
                                  {'Content-Length': '0', 'Content-Type': 'text/plain'})

    @responses.activate
    def test_get_application_by_app_id_happy_path(self):
        expected_app_id = '44444444-2943-1346-6c49-123456789abc'
        response_json = {"applicationName": "an_application_name",
                         "applicationShortName": "an_application_short_name",
                         "applicationTag": "an_application_tag", "description": "a_description",
                         "apiKey": "77788899-7059-11e8-82d1-aaaaaaaaaaaa",
                         "resourceURL":
                             f'{TEST_AF_URL}/registration/v2/{self.accountId}/applications/{expected_app_id}',
                         "useSmppInterface": False}

        callback = self.create_body_assertion(None, {'apiKey': self.apiKey}, response_json)
        responses.add_callback(responses.GET,
                               TEST_AF_URL + '/registration/v2/' + self.accountId + '/applications/'
                               + expected_app_id,
                               callback=callback
                               )

        result = aerframesdk.get_application_by_app_id(self.accountId, self.apiKey, expected_app_id,
                                                       self.verbose)
        self.assertEqual(response_json, result)

    @responses.activate
    def test_get_application_by_app_id_http_401(self):
        expected_application_id = '44444444-2943-1346-6c49-123456789abc'
        expected_response_headers = {'Content-Length': '0'}

        callback = self.create_empty_request_empty_response_assertion(401, expected_response_headers)
        responses.add_callback(responses.GET,
                               TEST_AF_URL + '/registration/v2/' + self.accountId + '/applications/'
                               + expected_application_id,
                               callback=callback
                               )

        with self.assertRaises(ApiException) as context:
            aerframesdk.get_application_by_app_id(self.accountId, self.apiKey, expected_application_id, self.verbose)
        # the requests - or responses - library likes adding a Content-Type header for an empty response body
        self.verify_api_exception(context.exception, 401, EMPTY_RESPONSE_BODY,
                                  {'Content-Length': '0', 'Content-Type': 'text/plain'})

    @responses.activate
    def test_create_application_happy_path(self):
        appShortName = 'an_app_short_name'
        appDescription = 'a_description'
        expected_request_body = {'applicationName': appShortName,
                                 'description': appDescription,
                                 'applicationShortName': appShortName,
                                 'applicationTag': appShortName}
        response_json = {"applicationName": appShortName,
                         "applicationShortName": appShortName,
                         "applicationTag": appShortName, "description": appDescription,
                         "apiKey": "77788899-7059-11e8-82d1-aaaaaaaaaaaa",
                         "resourceURL": TEST_AF_URL
                         + "/registration/v2/123/applications/12345678-1234-1234-1234-123456789abc",
                         "useSmppInterface": False}
        callback = self.create_body_assertion(expected_request_body, {'apiKey': self.apiKey},
                                              response_json, response_status=201)
        responses.add_callback(responses.POST,
                               TEST_AF_URL + '/registration/v2/' + self.accountId + '/applications',
                               callback=callback
                               )
        result = aerframesdk.create_application(self.accountId, self.apiKey, appShortName, appDescription, self.verbose)
        self.assertEqual(response_json, result)

    @responses.activate
    def test_create_application_http_401(self):
        expected_response_headers = {'Content-Length': '0'}
        appShortName = 'an_app_short_name'
        appDescription = 'a_description'
        expected_request_body = {'applicationName': appShortName,
                                 'description': appDescription,
                                 'applicationShortName': appShortName,
                                 'applicationTag': appShortName}

        callback = self.create_body_assertion(expected_request_body, {'apiKey': self.apiKey},
                                              EMPTY_RESPONSE_BODY, expected_response_headers, 401)
        responses.add_callback(responses.POST,
                               TEST_AF_URL + '/registration/v2/' + self.accountId + '/applications',
                               callback=callback
                               )

        with self.assertRaises(ApiException) as context:
            aerframesdk.create_application(self.accountId, self.apiKey, appShortName, appDescription, self.verbose)
        # the requests - or responses - library likes adding a Content-Type header for an empty response body
        self.verify_api_exception(context.exception, 401, EMPTY_RESPONSE_BODY,
                                  {'Content-Length': '0', 'Content-Type': 'text/plain'})

    @responses.activate
    def test_delete_application_happy_path(self):
        application_id = '44444444-2943-1346-6c49-123456789abc'

        callback = self.create_body_assertion(None, {'apiKey': self.apiKey},
                                              None, {}, 204)
        responses.add_callback(responses.DELETE,
                               TEST_AF_URL + '/registration/v2/' + self.accountId + '/applications/'
                               + application_id,
                               callback=callback)
        result = aerframesdk.delete_application(self.accountId, self.apiKey, application_id, self.verbose)
        self.assertTrue(result)

    @responses.activate
    def test_delete_application_http_404(self):
        application_id = '44444444-2943-1346-6c49-123456789abc'

        callback = self.create_empty_request_empty_response_assertion(404, {})
        responses.add_callback(responses.DELETE,
                               TEST_AF_URL + '/registration/v2/' + self.accountId + '/applications/'
                               + application_id,
                               callback=callback)
        result = aerframesdk.delete_application(self.accountId, self.apiKey, application_id, self.verbose)
        self.assertFalse(result)

    @responses.activate
    def test_delete_application_http_401(self):
        expected_application_id = '44444444-2943-1346-6c49-123456789abc'
        expected_response_headers = {'Content-Length': '0'}

        callback = self.create_empty_request_empty_response_assertion(401, expected_response_headers)
        responses.add_callback(responses.DELETE,
                               TEST_AF_URL + '/registration/v2/' + self.accountId + '/applications/'
                               + expected_application_id,
                               callback=callback
                               )

        with self.assertRaises(ApiException) as context:
            aerframesdk.delete_application(self.accountId, self.apiKey, expected_application_id, self.verbose)
        # the requests - or responses - library likes adding a Content-Type header for an empty response body
        self.verify_api_exception(context.exception, 401, EMPTY_RESPONSE_BODY,
                                  {'Content-Length': '0', 'Content-Type': 'text/plain'})

    @responses.activate
    def test_get_channel_id_by_application_tag_happy_path(self):
        expected_channel_id = '13245678-1234-1234-1234-123456789abc'
        wrong_channel_id = '87654321-4321-4321-4321-cba987654321'
        searchAppTag = "any_search_app_tag"
        response_body = {
            "notificationChannel": [
                {
                    "applicationTag": searchAppTag,
                    "channelType": "LongPolling",
                    "channelData": {
                        "channelURL":
                            f'{TEST_LP_URL}/notificationchannel/v2/{self.accountId}/longpoll/{expected_channel_id}',
                        "maxNotifications": 15
                    },
                    "callbackURL":
                        f'{TEST_AF_URL}/notificationchannel/v2/{self.accountId}/channels/{expected_channel_id}'
                        + '/callback',
                    "resourceURL":
                        f'{TEST_AF_URL}/notificationchannel/v2/{self.accountId}/channels/{expected_channel_id}',
                },
                {
                    "applicationTag": "anything but the searchAppTag",
                    "channelType": "LongPolling",
                    "channelData": {
                        "channelURL":
                            f'{TEST_LP_URL}/notificationchannel/v2/f{self.accountId}/longpoll/{wrong_channel_id}',
                        "maxNotifications": 15
                    },
                    "callbackURL":
                        f'{TEST_AF_URL}/notificationchannel/v2/{self.accountId}/channels/{wrong_channel_id}/callback',
                    "resourceURL": f'{TEST_AF_URL}/notificationchannel/v2/{self.accountId}/channels/{wrong_channel_id}',
                },
            ],
            "resourceURL": TEST_AF_URL + "/notificationchannel/v2/" + self.accountId + "/channels"
        }
        callback = self.create_body_assertion(None, {'apiKey': self.apiKey},
                                              response_body, response_status=200)
        responses.add_callback(responses.GET,
                               TEST_AF_URL + '/notificationchannel/v2/' + self.accountId + '/channels',
                               callback=callback
                               )
        result = aerframesdk.get_channel_id_by_tag(self.accountId, self.apiKey, searchAppTag, self.verbose)
        self.assertEqual(expected_channel_id, result)

    @responses.activate
    def test_get_channel_id_by_application_tag_not_found(self):
        channel_id_1 = '13245678-1234-1234-1234-123456789abc'
        channel_id_2 = '87654321-4321-4321-4321-cba987654321'
        searchAppTag = "any_search_app_tag"
        response_body = {
            "notificationChannel": [
                {
                    "applicationTag": searchAppTag + "a string to foil the search",
                    "channelType": "LongPolling",
                    "channelData": {
                        "channelURL": f'{TEST_LP_URL}/notificationchannel/v2/{self.accountId}/longpoll/{channel_id_1}',
                        "maxNotifications": 15
                    },
                    "callbackURL":
                        f'{TEST_AF_URL}/notificationchannel/v2/{self.accountId}/longpoll/{channel_id_1}/callback',
                    "resourceURL": f'{TEST_AF_URL}/notificationchannel/v2/{self.accountId}/longpoll/{channel_id_1}'
                },
                {
                    "applicationTag": "anything but the searchAppTag",
                    "channelType": "LongPolling",
                    "channelData": {
                        "channelURL": f'{TEST_LP_URL}/notificationchannel/v2/{self.accountId}/longpoll/{channel_id_2}',
                        "maxNotifications": 15
                    },
                    "callbackURL":
                        f'{TEST_AF_URL}/notificationchannel/v2/{self.accountId}/longpoll/{channel_id_2}/callback',
                    "resourceURL": f'{TEST_AF_URL}/notificationchannel/v2/{self.accountId}/longpoll/{channel_id_2}'
                },
            ],
            "resourceURL": TEST_AF_URL + "/notificationchannel/v2/" + self.accountId + "/channels"
        }
        callback = self.create_body_assertion(None, {'apiKey': self.apiKey},
                                              response_body, response_status=200)
        responses.add_callback(responses.GET,
                               TEST_AF_URL + '/notificationchannel/v2/' + self.accountId + '/channels',
                               callback=callback
                               )
        result = aerframesdk.get_channel_id_by_tag(self.accountId, self.apiKey, searchAppTag, self.verbose)
        self.assertIsNone(result)

    @responses.activate
    def test_get_channel_id_by_application_http_401(self):
        searchAppTag = 'an_application_tag'
        expected_response_headers = {'Content-Length': '0'}

        callback = self.create_empty_request_empty_response_assertion(401, expected_response_headers)
        responses.add_callback(responses.GET,
                               f'{TEST_AF_URL}/notificationchannel/v2/{self.accountId}/channels',
                               callback=callback
                               )

        with self.assertRaises(ApiException) as context:
            aerframesdk.get_channel_id_by_tag(self.accountId, self.apiKey, searchAppTag, self.verbose)
        # the requests - or responses - library likes adding a Content-Type header for an empty response body
        self.verify_api_exception(context.exception, 401, EMPTY_RESPONSE_BODY,
                                  {'Content-Length': '0', 'Content-Type': 'text/plain'})

    @responses.activate
    def test_get_channel(self):
        channel_id = '13245678-1234-1234-1234-123456789abc'
        response_body = {
            "applicationTag": "aerframe",
            "channelType": "LongPolling",
            "channelData": {
                "channelURL": f'{TEST_LP_URL}/notificationchannel/v2/{self.accountId}/longpoll/{channel_id}',
                "maxNotifications": 15
            },
            "callbackURL": TEST_AF_URL + "/notificationchannel/v2/20976/channels/" + channel_id + "/callback",
            "resourceURL": TEST_AF_URL + "/notificationchannel/v2/20976/channels/" + channel_id
        }
        callback = self.create_body_assertion(None, {'apiKey': self.apiKey},
                                              response_body, response_status=200)
        responses.add_callback(responses.GET,
                               f'{TEST_AF_URL}/notificationchannel/v2/{self.accountId}/channels/{channel_id}',
                               callback=callback
                               )
        result = aerframesdk.get_channel(self.accountId, self.apiKey, channel_id, self.verbose)
        self.assertEqual(response_body, result)

    @responses.activate
    def test_get_channel_http_404(self):
        channel_id = '13245678-1234-1234-1234-123456789abc'
        response_body = {
            "link": [],
            "serviceException": {
                "messageId": "SVC0004",
                "text": "No valid addresses provided in message part {0}",
                "variables": [
                    channel_id
                ]
            },
            "policyException": None
        }

        callback = self.create_body_assertion(None, {'apiKey': self.apiKey},
                                              response_body, response_status=404)
        responses.add_callback(responses.GET,
                               f'{TEST_AF_URL}/notificationchannel/v2/{self.accountId}/channels/{channel_id}',
                               callback=callback
                               )
        result = aerframesdk.get_channel(self.accountId, self.apiKey, channel_id, self.verbose)
        self.assertIsNone(result)

    @responses.activate
    def test_get_channel_http_401(self):
        channel_id = 'a_channel_id'
        expected_response_headers = {'Content-Length': '0'}

        callback = self.create_empty_request_empty_response_assertion(401, expected_response_headers)
        responses.add_callback(responses.GET,
                               TEST_AF_URL + '/notificationchannel/v2/' + self.accountId
                               + '/channels/' + channel_id,
                               callback=callback
                               )

        with self.assertRaises(ApiException) as context:
            aerframesdk.get_channel(self.accountId, self.apiKey, channel_id, self.verbose)
        # the requests - or responses - library likes adding a Content-Type header for an empty response body
        self.verify_api_exception(context.exception, 401, EMPTY_RESPONSE_BODY,
                                  {'Content-Length': '0', 'Content-Type': 'text/plain'})

    @responses.activate
    def test_create_channel_happy_path(self):
        application_tag = 'an_application_tag'
        response_channel_id = '1234578-1234-1234-1234-123456789abc'
        expected_body = {'applicationTag': application_tag,
                         'channelData': {'maxNotifications': '15',
                                         'type': 'nc:LongPollingData'},
                         'channelType': 'LongPolling'}
        response_body = {
            "applicationTag": application_tag,
            "channelType": "LongPolling",
            "channelData": {
                "channelURL": f'{TEST_LP_URL}/notificationchannel/v2/{self.accountId}/longpoll/{response_channel_id}',
                "maxNotifications": 15
            },
            "callbackURL":
                f'{TEST_AF_URL}/notificationchannel/v2/{self.accountId}/longpoll/{response_channel_id}/callback',
            "resourceURL": f'{TEST_AF_URL}/notificationchannel/v2/{self.accountId}/longpoll/{response_channel_id}'
        }

        callback = self.create_body_assertion(expected_body, {'apiKey': self.apiKey},
                                              response_body, response_status=200)
        responses.add_callback(responses.POST, TEST_AF_URL + '/notificationchannel/v2/' + self.accountId + '/channels',
                               callback=callback)
        result = aerframesdk.create_channel(self.accountId, self.apiKey, application_tag, self.verbose)
        self.assertEqual(result, response_body)

    @responses.activate
    def test_create_channel_http_401(self):
        application_tag = 'an_application_tag'
        response_channel_id = '1234578-1234-1234-1234-123456789abc'
        expected_body = {'applicationTag': application_tag,
                         'channelData': {'maxNotifications': '15',
                                         'type': 'nc:LongPollingData'},
                         'channelType': 'LongPolling'}

        expected_response_headers = {'Content-Length': '0'}
        callback = self.create_body_assertion(expected_body, {'apiKey': self.apiKey},
                                              EMPTY_RESPONSE_BODY, expected_response_headers, response_status=401)
        responses.add_callback(responses.POST, TEST_AF_URL + '/notificationchannel/v2/' + self.accountId + '/channels',
                               callback=callback)
        with self.assertRaises(ApiException) as context:
            aerframesdk.create_channel(self.accountId, self.apiKey, application_tag, self.verbose)
        # the requests - or responses - library likes adding a Content-Type header for an empty response body
        self.verify_api_exception(context.exception, 401, EMPTY_RESPONSE_BODY,
                                  {'Content-Length': '0', 'Content-Type': 'text/plain'})

    @responses.activate
    def test_delete_channel_happy_path(self):
        channel_id = '44444444-2943-1346-6c49-123456789abc'

        callback = self.create_empty_request_empty_response_assertion(204)
        responses.add_callback(responses.DELETE,
                               TEST_AF_URL + '/notificationchannel/v2/' + self.accountId + '/channels/'
                               + channel_id,
                               callback=callback
                               )

        result = aerframesdk.delete_channel(self.accountId, self.apiKey, channel_id, self.verbose)
        self.assertTrue(result)

    @responses.activate
    def test_delete_channel_http_404(self):
        channel_id = '44444444-2943-1346-6c49-123456789abc'
        response_body = {
            "link": [],
            "serviceException": {
                "messageId": "SVC0004",
                "text": "No valid addresses provided in message part {0}",
                "variables": [
                    channel_id
                ]
            },
            "policyException": None
        }

        callback = self.create_body_assertion(None, {'apiKey': self.apiKey},
                                              response_body, response_status=404)
        responses.add_callback(responses.DELETE,
                               TEST_AF_URL + '/notificationchannel/v2/' + self.accountId + '/channels/'
                               + channel_id,
                               callback=callback
                               )

        result = aerframesdk.delete_channel(self.accountId, self.apiKey, channel_id, self.verbose)
        self.assertFalse(result)

    @responses.activate
    def test_delete_channel_http_401(self):
        channel_id = '44444444-2943-1346-6c49-123456789abc'
        expected_response_headers = {'Content-Length': '0'}

        callback = self.create_empty_request_empty_response_assertion(401, expected_response_headers)
        responses.add_callback(responses.DELETE,
                               TEST_AF_URL + '/notificationchannel/v2/' + self.accountId + '/channels/'
                               + channel_id,
                               callback=callback
                               )

        with self.assertRaises(ApiException) as context:
            aerframesdk.delete_channel(self.accountId, self.apiKey, channel_id, self.verbose)
        # the requests - or responses - library likes adding a Content-Type header for an empty response body
        self.verify_api_exception(context.exception, 401, EMPTY_RESPONSE_BODY,
                                  {'Content-Length': '0', 'Content-Type': 'text/plain'})

    @responses.activate
    def test_get_inbound_subscriptions_by_app_short_name_happy_path(self):
        notify_channel_1 = '12345678-1234-1234-1234-123456789abc'
        notify_channel_2 = '87654321-4321-4321-4321-cba987654321'
        callback_data_1 = 'callback-data-1'
        callback_data_2 = 'callback-data-2'
        app_short_name_1 = 'app-1'
        app_short_name_2 = 'app-2'
        filter_1 = 'SP:a_service_profile'
        filter_2 = 'SP:*'
        subscription_id_1 = 'we-are-not-searching-for-this-one'
        subscription_id_2 = 'we-are-searching-for-this-one'
        response_body = {
            "subscription": [
                {
                    "callbackReference": {
                        "notifyURL":
                        f'{TEST_AF_URL}/notificationchannel/v2/{self.accountId}/channels/{notify_channel_1}/callback',
                        "callbackData": callback_data_1,
                        "notificationFormat": "JSON"
                    },
                    "destinationAddress": [
                        app_short_name_1
                    ],
                    "criteria": filter_1,
                    "resourceURL":
                    f'{TEST_AF_URL}/smsmessaging/v2/{self.accountId}/inbound/subscriptions//{subscription_id_1}'
                },
                {
                    "callbackReference": {
                        "notifyURL":
                        f'{TEST_AF_URL}/notificationchannel/v2/{self.accountId}/channels/{notify_channel_2}/callback',
                        "callbackData": callback_data_2,
                        "notificationFormat": "JSON"
                    },
                    "destinationAddress": [
                        app_short_name_2
                    ],
                    "criteria": filter_2,
                    "resourceURL":
                    f'{TEST_AF_URL}/smsmessaging/v2/{self.accountId}/inbound/subscriptions//{subscription_id_2}'
                }
            ],
            "resourceURL": f'{TEST_AF_URL}/smsmessaging/v2/{self.accountId}/inbound/subscriptions/'
        }

        callback = self.create_body_assertion(None, {'apiKey': self.apiKey}, response_body)
        responses.add_callback(responses.GET,
                               f'{TEST_AF_URL}/smsmessaging/v2/{self.accountId}/inbound/subscriptions',
                               callback=callback)
        result = aerframesdk.get_inbound_subscription_by_app_short_name(self.accountId, self.apiKey,
                                                                        app_short_name_2, self.verbose)

        self.assertEqual(result, subscription_id_2)

    @responses.activate
    def test_get_inbound_subscription_by_app_short_name_none_found(self):
        notify_channel_1 = '12345678-1234-1234-1234-123456789abc'
        notify_channel_2 = '87654321-4321-4321-4321-cba987654321'
        callback_data_1 = 'callback-data-1'
        callback_data_2 = 'callback-data-2'
        app_short_name_1 = 'app-1'
        app_short_name_2 = 'app-2'
        filter_1 = 'SP:a_service_profile'
        filter_2 = 'SP:*'
        subscription_id_1 = 'we-are-not-searching-for-this-one'
        subscription_id_2 = 'we-are-searching-for-this-one'
        response_body = {
            "subscription": [
                {
                    "callbackReference": {
                        "notifyURL": f'{TEST_AF_URL}/notificationchannel/v2/{self.accountId}/channels/'
                                     f'{notify_channel_1}/callback',
                        "callbackData": callback_data_1,
                        "notificationFormat": "JSON"
                    },
                    "destinationAddress": [
                        app_short_name_1
                    ],
                    "criteria": filter_1,
                    "resourceURL":
                        f'{TEST_AF_URL}/smsmessaging/v2/{self.accountId}/inbound/subscriptions//{subscription_id_1}'
                },
                {
                    "callbackReference": {
                        "notifyURL": f'{TEST_AF_URL}/notificationchannel/v2/{self.accountId}/channels/'
                        + f'{notify_channel_2}/callback',
                        "callbackData": callback_data_2,
                        "notificationFormat": "JSON"
                    },
                    "destinationAddress": [
                        app_short_name_2
                    ],
                    "criteria": filter_2,
                    "resourceURL":
                        f'{TEST_AF_URL}/smsmessaging/v2/{self.accountId}/inbound/subscriptions//{subscription_id_2}'
                }
            ],
            "resourceURL": f'{TEST_AF_URL}/smsmessaging/v2/{self.accountId}/inbound/subscriptions/'
        }

        callback = self.create_body_assertion(None, {'apiKey': self.apiKey}, response_body)
        responses.add_callback(responses.GET,
                               f'{TEST_AF_URL}/smsmessaging/v2/{self.accountId}/inbound/subscriptions',
                               callback=callback)
        result = aerframesdk.get_inbound_subscription_by_app_short_name(self.accountId, self.apiKey,
                                                                        'peoiruqpweoirjnqwoeirjqpwo', self.verbose)

        self.assertIsNone(result)

    @responses.activate
    def test_get_inbound_subscription_by_app_short_name_zero_returned(self):
        app_short_name_2 = 'app-2'
        response_body = {
            "subscription": [],
            "resourceURL": f'{TEST_AF_URL}/smsmessaging/v2/{self.accountId}/inbound/subscriptions/'
        }

        callback = self.create_body_assertion(None, {'apiKey': self.apiKey}, response_body)
        responses.add_callback(responses.GET,
                               f'{TEST_AF_URL}/smsmessaging/v2/{self.accountId}/inbound/subscriptions',
                               callback=callback)
        result = aerframesdk.get_inbound_subscription_by_app_short_name(self.accountId, self.apiKey,
                                                                        app_short_name_2, self.verbose)

        self.assertIsNone(result)

    @responses.activate
    def test_get_inbound_subscriptions_http_401(self):
        app_short_name = 'my_app_short_name'
        callback = self.create_empty_request_empty_response_assertion(response_status=401,
                                                                      response_headers={'Content-Length': '0'})
        responses.add_callback(responses.GET,
                               f'{TEST_AF_URL}/smsmessaging/v2/{self.accountId}/inbound/subscriptions',
                               callback=callback)

        with self.assertRaises(ApiException) as context:
            aerframesdk.get_inbound_subscription_by_app_short_name(self.accountId, self.apiKey,
                                                                   app_short_name, self.verbose)
        self.verify_api_exception(context.exception, 401, EMPTY_RESPONSE_BODY,
                                  {'Content-Length': '0', 'Content-Type': 'text/plain'})

    @responses.activate
    def test_get_outbound_subscription_id_by_app_name_happy_path(self):
        app_short_name = 'any_short_name'
        notification_channel_id = '12345678-1234-1234-1234-123456789abc'
        subscription_id = '87654321-4321-4321-4321-cba987654321'
        callback_data = 'my_callback_data'
        filter_criteria = 'SP:SOME_SERVICE_PROFILE'
        response_body = {
            "resourceURL": f'{TEST_AF_URL}/smsmessaging/v2/{self.accountId}/outbound/{app_short_name}/subscriptions',
            "deliveryReceiptSubscription": [
                {
                    "callbackReference": {
                        "notifyURL": f'{TEST_AF_URL}/notificationchannel/v2/{self.accountId}/'
                        + f'channels/{notification_channel_id}/callback',
                        "callbackData": callback_data,
                        "notificationFormat": "JSON"
                    },
                    "filterCriteria": filter_criteria,
                    "resourceURL":
                        f'{TEST_AF_URL}smsmessaging/v2/{self.accountId}/outbound/{app_short_name}/'
                        + f'subscriptions/{subscription_id}'
                }
            ]
        }
        callback = self.create_body_assertion(None, {'apiKey': self.apiKey}, response_body)
        responses.add_callback(responses.GET,
                               TEST_AF_URL + '/smsmessaging/v2/' + self.accountId + '/outbound/' + app_short_name
                               + '/subscriptions',
                               callback=callback
                               )
        result = aerframesdk.get_outbound_subscription_id_by_app_short_name(self.accountId, self.apiKey, app_short_name,
                                                                            self.verbose)
        self.assertEqual(subscription_id, result)

    @responses.activate
    def test_get_outbound_subscription_id_by_app_name_not_found(self):
        app_short_name = 'any_short_name'
        response_body = {
            'resourceUrl': f'{TEST_AF_URL}/smsmessaging/v2/{self.accountId}/outbound/{app_short_name}/subscriptions'
        }
        callback = self.create_body_assertion(None, {'apiKey': self.apiKey}, response_body)
        responses.add_callback(responses.GET,
                               TEST_AF_URL + '/smsmessaging/v2/' + self.accountId + '/outbound/' + app_short_name
                               + '/subscriptions',
                               callback=callback
                               )
        result = aerframesdk.get_outbound_subscription_id_by_app_short_name(self.accountId, self.apiKey, app_short_name,
                                                                            self.verbose)
        self.assertIsNone(result)

    @responses.activate
    def test_get_outbound_subscription_id_by_app_name_http_401(self):
        app_short_name = 'any_short_name'
        expected_response_headers = {'Content-Length': '0'}

        callback = self.create_empty_request_empty_response_assertion(401, expected_response_headers)
        responses.add_callback(responses.GET,
                               TEST_AF_URL + '/smsmessaging/v2/' + self.accountId + '/outbound/'
                               + app_short_name + '/subscriptions',
                               callback=callback
                               )

        with self.assertRaises(ApiException) as context:
            aerframesdk.get_outbound_subscription_id_by_app_short_name(self.accountId,
                                                                       self.apiKey, app_short_name, self.verbose)
        # the requests - or responses - library likes adding a Content-Type header for an empty response body
        self.verify_api_exception(context.exception, 401, EMPTY_RESPONSE_BODY,
                                  {'Content-Length': '0', 'Content-Type': 'text/plain'})

    @responses.activate
    def test_get_outbound_subscription_happy_path(self):
        subscription_id = '12345678-1234-1234-1234-123456789abc'
        notification_channel_id = '11111111-1111-1111-1111-123456789abc'
        app_short_name = 'some_short_name'
        response_body = {
            "callbackReference": {
                "notifyURL":
                f'{TEST_AF_URL}/notificationchannel/v2/{self.accountId}/channels/{notification_channel_id}/callback',
                "callbackData": "some_callback_data",
                "notificationFormat": "JSON"
            },
            "filterCriteria": "SP:*",
            "resourceURL":
            f'{TEST_AF_URL}/smsmessaging/v2/{self.accountId}/outbound/{app_short_name}/subscriptions/{subscription_id}'
        }

        callback = self.create_body_assertion(None, {'apiKey': self.apiKey}, response_body)
        responses.add_callback(responses.GET,
                               f'{TEST_AF_URL}/smsmessaging/v2/{self.accountId}/outbound/{app_short_name}/' +
                               f'subscriptions/{subscription_id}',
                               callback=callback)
        result = aerframesdk.get_outbound_subscription(self.accountId, self.apiKey, app_short_name, subscription_id,
                                                       self.verbose)
        self.assertEqual(response_body, result)

    @responses.activate
    def test_get_outbound_subscription_http_404(self):
        app_short_name = 'a_short_name'
        subscription_id = '00000000-0000-0000-0000-000000000000'
        response_body = {
            "link": [],
            "serviceException": {
                "messageId": "SVC0004",
                "text": "No valid addresses provided in message part {0}",
                "variables": [
                    subscription_id
                ]
            },
            "policyException": None
        }
        callback = self.create_body_assertion(None, {'apiKey': self.apiKey}, response_body, response_status=404)
        responses.add_callback(responses.GET,
                               TEST_AF_URL + '/smsmessaging/v2/' + self.accountId + '/outbound/' + app_short_name
                               + '/subscriptions/' + subscription_id,
                               callback=callback
                               )
        result = aerframesdk.get_outbound_subscription(self.accountId, self.apiKey, app_short_name, subscription_id,
                                                       self.verbose)
        self.assertIsNone(result)

    @responses.activate
    def test_get_outbound_subscription_http_401(self):
        app_short_name = 'a_short_name'
        subscription_id = '00000000-0000-0000-0000-000000000000'

        callback = self.create_empty_request_empty_response_assertion(401, {'Content-length': '0'})
        responses.add_callback(responses.GET,
                               TEST_AF_URL + '/smsmessaging/v2/' + self.accountId + '/outbound/' + app_short_name
                               + '/subscriptions/' + subscription_id,
                               callback=callback
                               )
        with self.assertRaises(ApiException) as context:
            aerframesdk.get_outbound_subscription(self.accountId, self.apiKey, app_short_name, subscription_id,
                                                  self.verbose)
        # the requests - or responses - library likes adding a Content-Type header for an empty response body
        self.verify_api_exception(context.exception, 401, EMPTY_RESPONSE_BODY,
                                  {'Content-Length': '0', 'Content-Type': 'text/plain'})

    @responses.activate
    def test_delete_outbound_subscription_happy_path(self):
        app_short_name = 'a_short_name'
        subscription_id = '00000000-0000-0000-0000-000000000000'
        response_body = ''
        callback = self.create_body_assertion(None, {'apiKey': self.apiKey}, response_body, response_status=204)
        responses.add_callback(responses.DELETE,
                               TEST_AF_URL + '/smsmessaging/v2/' + self.accountId + '/outbound/' + app_short_name
                               + '/subscriptions/' + subscription_id,
                               callback=callback
                               )
        result = aerframesdk.delete_outbound_subscription(self.accountId, self.apiKey, app_short_name,
                                                          subscription_id, self.verbose)
        self.assertTrue(result)

    @responses.activate
    def test_delete_outbound_subscription_not_found(self):
        app_short_name = 'a_short_name'
        subscription_id = '00000000-0000-0000-0000-000000000000'
        response_body = {
            "link": [],
            "serviceException": {
                "messageId": "SVC0004",
                "text": "No valid addresses provided in message part {0}",
                "variables": [
                    subscription_id
                ]
            },
            "policyException": None
        }
        callback = self.create_body_assertion(None, {'apiKey': self.apiKey}, response_body, response_status=404)
        responses.add_callback(responses.DELETE,
                               TEST_AF_URL + '/smsmessaging/v2/' + self.accountId + '/outbound/' + app_short_name
                               + '/subscriptions/' + subscription_id,
                               callback=callback
                               )
        result = aerframesdk.delete_outbound_subscription(self.accountId, self.apiKey, app_short_name,
                                                          subscription_id, self.verbose)
        self.assertFalse(result)

    @responses.activate
    def test_delete_outbound_subscription_http_401(self):
        app_short_name = 'a_short_name'
        subscription_id = '00000000-0000-0000-0000-000000000000'

        callback = self.create_empty_request_empty_response_assertion(401, {'Content-length': '0'})
        responses.add_callback(responses.DELETE,
                               TEST_AF_URL + '/smsmessaging/v2/' + self.accountId + '/outbound/' + app_short_name
                               + '/subscriptions/' + subscription_id,
                               callback=callback
                               )
        with self.assertRaises(ApiException) as context:
            aerframesdk.delete_outbound_subscription(self.accountId, self.apiKey, app_short_name, subscription_id,
                                                     self.verbose)
        # the requests - or responses - library likes adding a Content-Type header for an empty response body
        self.verify_api_exception(context.exception, 401, EMPTY_RESPONSE_BODY,
                                  {'Content-Length': '0', 'Content-Type': 'text/plain'})

    @responses.activate
    def test_create_outbound_subscription_happy_path(self):
        app_short_name = 'an_app_short_name'
        app_channel_id = '12345678-1234-5678-9abc-123456789abc'
        subscription_id = '87654321-1234-4321-1234-cba987654321'
        filter_criteria = 'SP:*'
        callback_reference = {
            'callbackData': app_short_name + '-mt',
            'notifyURL': TEST_AF_URL + '/notificationchannel/v2/'
            + self.accountId + '/channels/' + app_channel_id + '/callback'
        }
        expected_request_body = {'callbackReference': callback_reference,
                                 # TODO: this will need to change to let the user specify their own filter criteria
                                 'filterCriteria': filter_criteria,
                                 'destinationAddress': [app_short_name]}

        response_callback_reference = copy.deepcopy(callback_reference)
        response_callback_reference['notificationFormat'] = 'JSON'
        response_body = {
            'callbackReference': response_callback_reference,
            'filterCriteria': filter_criteria,
            'resourceURL': f'{TEST_AF_URL}/smsmessaging/v2/{self.accountId}/' +
                           f'outbound/{app_short_name}/subscriptions/{subscription_id}'
        }
        callback = self.create_body_assertion(expected_request_body, {'apiKey': self.apiKey},
                                              response_body, response_status=201)
        responses.add_callback(responses.POST,
                               f'{TEST_AF_URL}/smsmessaging/v2/{self.accountId}/outbound/'
                               + f'{app_short_name}/subscriptions',
                               callback=callback)
        result = aerframesdk.create_outbound_subscription(self.accountId, self.apiKey, app_short_name,
                                                          app_channel_id, self.verbose)

        self.assertEqual(result, response_body)

    @responses.activate
    def test_create_outbound_subscription_http_401(self):
        app_short_name = 'an_app_short_name'
        app_channel_id = '12345678-1234-5678-9abc-123456789abc'
        subscription_id = '87654321-1234-4321-1234-cba987654321'
        filter_criteria = 'SP:*'
        callback_reference = {
            'callbackData': app_short_name + '-mt',
            'notifyURL':
            TEST_AF_URL + '/notificationchannel/v2/' + self.accountId + '/channels/' + app_channel_id + '/callback'
        }
        expected_request_body = {'callbackReference': callback_reference,
                                 # TODO: this will need to change to let the user specify their own filter criteria
                                 'filterCriteria': filter_criteria,
                                 'destinationAddress': [app_short_name]}

        expected_response_headers = {'Content-Length': '0'}

        callback = self.create_body_assertion(expected_request_body, {'apiKey': self.apiKey},
                                              '', expected_response_headers, response_status=401)
        responses.add_callback(responses.POST,
                               TEST_AF_URL + '/smsmessaging/v2/' + self.accountId + '/outbound/'
                               + app_short_name + '/subscriptions',
                               callback=callback
                               )

        with self.assertRaises(ApiException) as context:
            aerframesdk.create_outbound_subscription(self.accountId, self.apiKey, app_short_name,
                                                     app_channel_id, self.verbose)
        # the requests - or responses - library likes adding a Content-Type header for an empty response body
        self.verify_api_exception(context.exception, 401, EMPTY_RESPONSE_BODY,
                                  {'Content-Length': '0', 'Content-Type': 'text/plain'})

    @responses.activate
    def test_get_location_happy_path(self):
        response_body = {
            "responseType": "Cell ID",
            "mcc": 0,
            "mnc": 0,
            "lac": 0,
            "cellId": 0,
            "locationTimestamp": 0.0,
            "ageOfLocation": 0,
            "state": 0,
            "requestId": "01234567-0123-0123-0123-0123456789ab",
            "destinationType": "CS",
            "destinationTypeCode": 7
        }
        callback = self.create_body_assertion(None, {'apiKey': self.apiKey}, response_body, response_status=200)
        responses.add_callback(responses.GET,
                               f'{TEST_AF_URL}/networkservices/v2/{self.accountId}/devices/{self.deviceIdType}/'
                               + f'{self.deviceId}/networkLocation',
                               callback=callback)
        result = aerframesdk.get_location(self.accountId, self.apiKey, self.deviceIdType, self.deviceId, self.verbose)
        self.assertEqual(response_body, result)

    @responses.activate
    def test_get_location_http_404(self):

        response_body = {
            "link": [],
            "serviceException": {
                "messageId": "SVC0002",
                "text": "Invalid input value for message part {0}",
                "variables": [
                    "SE0010(Device does not exist!)"
                ]
            },
            "policyException": None
        }

        callback = self.create_body_assertion(None, {'apiKey': self.apiKey}, response_body, response_status=404)
        responses.add_callback(responses.GET,
                               f'{TEST_AF_URL}/networkservices/v2/{self.accountId}/devices/{self.deviceIdType}/'
                               + f'{self.deviceId}/networkLocation',
                               callback=callback)

        with self.assertRaises(ApiException) as context:
            aerframesdk.get_location(self.accountId, self.apiKey, self.deviceIdType, self.deviceId, self.verbose)
        # the requests - or responses - library likes adding a Content-Type header for an empty response body
        self.verify_api_exception(context.exception, 404, json.dumps(response_body))

    @responses.activate
    def test_send_mt_sms_happy_path(self):
        imsi = '123456789012345'
        app_short_name = 'a_short_name'
        smsText = 'command:omega_protocol:enable'
        resource_id = '12345678-1234-1234-1234-123456789abc'
        request_body = {
            "address": [
                imsi
            ],
            "senderAddress": app_short_name,
            "outboundSMSTextMessage": {
                "message": smsText
            },
            "clientCorrelator": "123456",
            "senderName": app_short_name
        }
        response_body = copy.deepcopy(request_body)
        response_body['resourceURL'] =\
            f'{TEST_AF_URL}/smsmessaging/v2/{self.accountId}/outbound/{app_short_name}/requests/{resource_id}'

        callback = self.create_body_assertion(request_body, {'apiKey': self.apiKey}, response_body, response_status=201)
        responses.add_callback(responses.POST,
                               f'{TEST_AF_URL}/smsmessaging/v2/{self.accountId}/outbound/{app_short_name}/requests',
                               callback=callback)
        result = aerframesdk.send_mt_sms(self.accountId, self.apiKey, app_short_name, imsi, smsText, self.verbose)

        self.assertEqual(response_body, result)

    @responses.activate
    def test_send_mt_sms_http_401(self):
        imsi = '123456789012345'
        app_short_name = 'another_short_name'
        smsText = 'command:omega_protocol:halt'
        request_body = {
            "address": [
                imsi
            ],
            "senderAddress": app_short_name,
            "outboundSMSTextMessage": {
                "message": smsText
            },
            "clientCorrelator": "123456",
            "senderName": app_short_name
        }
        callback = self.create_body_assertion(request_body, {'apiKey': self.apiKey}, '', {'Content-Length': '0'},
                                              response_status=401)
        responses.add_callback(responses.POST,
                               f'{TEST_AF_URL}/smsmessaging/v2/{self.accountId}/outbound/{app_short_name}/requests',
                               callback=callback)
        with self.assertRaises(ApiException) as context:
            aerframesdk.send_mt_sms(self.accountId, self.apiKey, app_short_name, imsi, smsText, self.verbose)
        # the requests - or responses - library likes adding a Content-Type header for an empty response body
        self.verify_api_exception(context.exception, 401, EMPTY_RESPONSE_BODY,
                                  {'Content-Length': '0', 'Content-Type': 'text/plain'})

    @responses.activate
    def test_send_mt_sms_http_404(self):
        imsi = '123456789012345'
        app_short_name = 'a_short_name'
        smsText = 'command:omega_protocol:enable'
        resource_id = '12345678-1234-1234-1234-123456789abc'
        request_body = {
            "address": [
                imsi
            ],
            "senderAddress": app_short_name,
            "outboundSMSTextMessage": {
                "message": smsText
            },
            "clientCorrelator": "123456",
            "senderName": app_short_name
        }
        response_body = {
            "link": [],
            "serviceException": {
                "messageId": "SVC0002",
                "text": "Invalid input value for message part {0}",
                "variables": [
                    "SE0010(Device does not exist!)"
                ]
            },
            "policyException": None
        }

        callback = self.create_body_assertion(request_body, {'apiKey': self.apiKey}, response_body, response_status=404)
        responses.add_callback(responses.POST,
                               f'{TEST_AF_URL}/smsmessaging/v2/{self.accountId}/outbound/{app_short_name}/requests',
                               callback=callback)
        result = aerframesdk.send_mt_sms(self.accountId, self.apiKey, app_short_name, imsi, smsText, self.verbose)

        self.assertIsNone(result)

    @responses.activate
    def test_poll_notification_channel_happy_path(self):
        longpoll_channel_id = '11111111-2222-3333-4444-555555555555'
        channel_url = f'{TEST_LP_URL}/notificationchannel/v2/{self.accountId}/longpoll/{longpoll_channel_id}'
        notification_1_id = '01234567-0123-0123-0123-0123456789ab'
        notification_2_id = '76543210-3210-3210-3210-ba9876543210'
        subscription_id = '12345678-1234-4321-1234-123456789abc'
        app_short_name = 'my-app-short-name'
        response_body = {
            "deliveryInfoNotification": [
                {
                    "callbackData": "your-callback-data",
                    "deliveryInfo": [
                        {
                            "address": "123456789012345",
                            "deliveryStatus": "DeliveredToTerminal",
                            "link": [
                                {
                                    "rel": "MTMessageRequest ResourceUrl",
                                    "href": f'{TEST_AF_URL}/smsmessaging/v2/{self.accountId}/outbound/'
                                    + f'{app_short_name}/requests/{notification_1_id}'
                                },
                                {
                                    "rel": "MTDeliverySubscription ResourceUrl",
                                    "href": f'{TEST_AF_URL}/smsmessaging/v2/{self.accountId}/outbound/'
                                    + f'{app_short_name}/subscriptions/{subscription_id}'
                                }
                            ]
                        },
                        {
                            "address": "123456789012345",
                            "deliveryStatus": "DeliveryImpossible",
                            "description": "-9:Location unknown.",
                            "link": [
                                {
                                    "rel": "MTMessageRequest ResourceUrl",
                                    "href": f'{TEST_AF_URL}/smsmessaging/v2/{self.accountId}/outbound/'
                                    + f'{app_short_name}/requests/{notification_2_id}'
                                },
                                {
                                    "rel": "MTDeliverySubscription ResourceUrl",
                                    "href": f'{TEST_AF_URL}/smsmessaging/v2/{self.accountId}/outbound/'
                                    + f'{app_short_name}/subscriptions/{subscription_id}'
                                }
                            ]
                        }
                    ]
                }
            ],
            'inboundSMSMessageNotification': [
                {
                    "callbackData": "your-callback-data",
                    "inboundSMSMessage": {
                        "destinationAddress": "23747",
                        "senderAddress": "123456789012345",
                        "message": "U3BvdHRlZCBNYWMgMDQ6Mjk6MTE6NDU6Nzg6ZGUgYXQgMjAyMC0wMy0xMVQxNjo0MzoyOS4xMjNa",
                        "dateTime": "2020-03-11T16:43:33.307Z",
                        "link": [
                            {
                                "rel": "MOSubscription ResourceUrl",
                                "href": f'{TEST_AF_URL}/smsmessaging/v2/{self.accountId}/inbound/'
                                + f'subscriptions/{subscription_id}'
                            }
                        ],
                        "messageId": "21812345-0000-0000-009a-54321123454d",
                        "encodingScheme": "7-Bit",
                        "serviceCode": "12345"
                    }
                }
            ]
        }

        callback = self.create_body_assertion(None, {'apiKey': self.apiKey}, response_body, response_status=200)
        responses.add_callback(responses.GET,
                               channel_url,
                               callback=callback)
        result = aerframesdk.poll_notification_channel(self.accountId, self.apiKey, channel_url, self.verbose)

        self.assertEqual(response_body, result)

    @responses.activate
    def test_poll_notification_channel_http_401(self):
        longpoll_channel_id = '11111111-2222-3333-4444-555555555555'
        channel_url = f'{TEST_LP_URL}/notificationchannel/v2/{self.accountId}/longpoll/{longpoll_channel_id}'
        response_body = 'Access Denied: No account associated with the given Api Key!'
        callback = self.create_body_assertion(None, {'apiKey': self.apiKey}, response_body,
                                              {'Content-Type': 'text/plain'}, response_status=401)
        responses.add_callback(responses.GET,
                               channel_url,
                               callback=callback)
        with self.assertRaises(ApiException) as context:
            aerframesdk.poll_notification_channel(self.accountId, self.apiKey, channel_url, self.verbose)
        # the requests - or responses - library likes adding a Content-Type header for an empty response body
        self.verify_api_exception(context.exception, 401, response_body,
                                  {'Content-Type': 'text/plain'})
