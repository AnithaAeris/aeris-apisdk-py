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

import json
import unittest

from unittest.mock import Mock

import aerisapisdk.aerisconfig as aerisconfig
import aerisapisdk.aeradminsdk as aeradminsdk
from aerisapisdk.exceptions import ApiException

import responses

from tests.AerTestCase import AerTestCase

# AerAdmin URL for testing -- pretend that aerisconfig always points to this URL
TEST_AERADMIN_URL = 'https://localhost'
aerisconfig.get_aeradmin_url = Mock(return_value=TEST_AERADMIN_URL)


class TestAerAdminSDK(AerTestCase):
    accountId = '1'
    apiKey = 'anApiKey'
    email = 'foo@bar.com'
    deviceIdType = 'IMSI'
    deviceId = '123456789012345'
    verbose = False

    def test_get_aeradmin_base(self):
        base = aeradminsdk.get_aeradmin_base()
        self.assertEqual(TEST_AERADMIN_URL + '/', base)

    @responses.activate
    def test_get_device_details_happy_path(self):
        response_json = {
            "transactionID": "deadbeef-5cc0-11ea-b9ea-feedcafe1234",
            "resultCode": 0,
            "resultMessage": "OK",
            "opCompletionTimestamp": "2020-01-01T00:00:00.000Z",
            "deviceProfileId": "AER0000012345678",
            "deviceAttributes": [
                {
                    "result": {
                        "resultCode": 0,
                        "resultMessage": "OK"
                    },
                    "deviceID": {
                        "iccId": "8918123412341234123",
                        "msisdn": "11123456789",
                        "imsi": self.deviceId
                    },
                    "technology": "GSM",
                    "serviceName": "service_name_here",
                    "deviceStatus": "Bill",
                    "activationDate": "2019-01-01T00:00:00.000Z",
                    "cancelCode": 0,
                    "ratePlan": "rate_plan_identifier",
                    "ratePlanLabel": "rate_plan_label",
                    "softwareVersion": "2.1.7.8",
                    "active": True,
                    "lteOnly": False
                }
            ],
            "applicationType": "M",
            "customField": {},
            "reportGroup": 0,
            "containerId": "",
            "dataModelId": "",
            "registerOnAerCloud": False
        }

        expected_request_body = {"accountID": self.accountId, "email": self.email, self.deviceIdType: self.deviceId}
        callback = self.create_body_assertion(expected_request_body, None, response_json)
        responses.add_callback(responses.POST,
                               TEST_AERADMIN_URL+'/AerAdmin_WS_5_0/rest/devices/details?apiKey='+self.apiKey,
                               callback=callback
                               )
        result = aeradminsdk.get_device_details(self.accountId, self.apiKey, self.email, self.deviceIdType,
                                                self.deviceId, self.verbose)

        self.assertEqual(response_json, result)

    @responses.activate
    def test_get_device_details_http_401(self):
        response_json = {
            "code": 401, "status": "UNAUTHORIZED", "message": "AccountId and ApiKey are not linked."
        }
        expected_request_body = {"accountID": self.accountId, "email": self.email, self.deviceIdType: self.deviceId}
        callback = self.create_body_assertion(expected_request_body, None, response_json, response_status=401)
        responses.add_callback(responses.POST,
                               TEST_AERADMIN_URL + '/AerAdmin_WS_5_0/rest/devices/details?apiKey=' + self.apiKey,
                               callback=callback
                               )
        with self.assertRaises(ApiException) as context:
            aeradminsdk.get_device_details(self.accountId, self.apiKey, self.email, self.deviceIdType,
                                           self.deviceId, self.verbose)
        self.verify_api_exception(context.exception, 401, json.dumps(response_json))

    @responses.activate
    def test_get_device_details_device_not_activated(self):
        response_json = {
            "transactionID": "12345678-5cd2-11ea-b9ea-123456789abc",
            "resultCode": 1047,
            "resultMessage": "Device not Activated.",
            "opCompletionTimestamp": None
        }

        expected_request_body = {"accountID": self.accountId, "email": self.email, self.deviceIdType: self.deviceId}
        callback = self.create_body_assertion(expected_request_body, None, response_json, response_status=200)
        responses.add_callback(responses.POST,
                               TEST_AERADMIN_URL + '/AerAdmin_WS_5_0/rest/devices/details?apiKey=' + self.apiKey,
                               callback=callback
                               )
        with self.assertRaises(ApiException) as context:
            aeradminsdk.get_device_details(self.accountId, self.apiKey, self.email, self.deviceIdType,
                                           self.deviceId, self.verbose)
        self.verify_api_exception(context.exception, 200, json.dumps(response_json))
        # assert that the result code -- from the body of the response -- is in the exception message
        self.assertTrue('1047' in context.exception.message)

    @responses.activate
    def test_get_network_details_happy_path(self):
        response_json = {
            "deviceProfileId": "AER0000012345678",
            "transactionID": "beefbeef-5ce1-11ea-bad2-beefbeefbeef",
            "resultCode": 0,
            "resultMessage": "OK",
            "opCompletionTimestamp": "2020-01-01T00:00:00.000Z",
            "networkResponse": [
                {
                    "ICCID": "89185015061234567890",
                    "IMSI": "123451234567890",
                    "MDN": "12312345678",
                    "MSISDN": "12345678901",
                    "dataSession": {
                        "serviceType": "UTRAN 3G / GERAN 2G",
                        "lastStartTime": "2019-12-31T01:49:44.000Z",
                        "lastStopTime": "2019-12-21T02:12:22.000Z"
                    },
                    "registration": {
                        "isRegistered": True,
                        "lastInactiveTime": "2019-12-22T07:33:50.000Z",
                        "lastRegistrationTime": "2019-12-21T03:00:00.000Z",
                        "lastRegistrationLocation": "14044558050",
                        "lastVoiceMTTime": "2019-02-14T23:00:50.000Z",
                        "lastSmsMOTime": "2019-11-07T23:52:59.000Z",
                        "lastSmsMTTime": "2019-11-28T19:00:00.000Z",
                        "lastSGSNLocation": "15622751147",
                        "lastAuthorizationTime": "2019-12-31T01:49:39.000Z"
                    }
                }
            ],
            "activeProfile": {
                "ICCID": "89185015061234567890",
                "IMSI": "123451234567890",
                "MDN": "12312345678",
                "MSISDN": "12345678901",
                "technology": "GSM"
            }
        }
        expected_request_body = None
        expected_query_params = {"accountID": self.accountId,
                                 "email": self.email,
                                 self.deviceIdType: self.deviceId,
                                 "apiKey": self.apiKey}
        callback = self.create_body_assertion(expected_request_body, expected_query_params, response_json)
        responses.add_callback(responses.GET,
                               TEST_AERADMIN_URL + '/AerAdmin_WS_5_0/rest/devices/network/details',
                               callback=callback,
                               match_querystring=False
                               )
        result = aeradminsdk.get_device_network_details(self.accountId, self.apiKey, self.email, self.deviceIdType,
                                                        self.deviceId, self.verbose)

        self.assertEqual(response_json, result)

    @responses.activate
    def test_get_network_details_http_401(self):
        response_json = {
            "code": 401, "status": "UNAUTHORIZED", "message": "AccountId and ApiKey are not linked."
        }
        expected_query_params = {"accountID": self.accountId,
                                 "email": self.email,
                                 self.deviceIdType: self.deviceId,
                                 "apiKey": self.apiKey}
        callback = self.create_body_assertion(None, expected_query_params, response_json, response_status=401)
        responses.add_callback(responses.GET,
                               TEST_AERADMIN_URL + '/AerAdmin_WS_5_0/rest/devices/network/details',
                               callback=callback,
                               match_querystring=False
                               )
        with self.assertRaises(ApiException) as context:
            aeradminsdk.get_device_network_details(self.accountId, self.apiKey, self.email, self.deviceIdType,
                                                   self.deviceId, self.verbose)
        self.verify_api_exception(context.exception, 401, json.dumps(response_json))
