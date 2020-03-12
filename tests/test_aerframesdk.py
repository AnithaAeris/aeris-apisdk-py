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
