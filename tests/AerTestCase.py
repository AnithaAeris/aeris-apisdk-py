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


class AerTestCase(unittest.TestCase):
    __default_response_headers = {'Content-Type': 'application/json'}
    """
    A class with basic methods for testing HTTP API calls.
    """
    def create_empty_request_empty_response_assertion(self, response_status,
                                                      response_headers=__default_response_headers):
        """
        Creates a "responses" callback that checks that the request body is non-existent, and that produces
        an empty response body with a status code equal to the given response_status.
        Assumes that the request will be sending a query parameter 'apiKey' with value equal to your subclass' apiKey
        Parameters
        ----------
        response_status
        response_headers: obj
            the headers you want the response to have

        Returns
        -------

        """
        return self.create_body_assertion(None, {'apiKey': self.apiKey}, '', response_headers,
                                          response_status=response_status)

    def create_body_assertion(self, expected_request_body, expected_request_query_params, response_body,
                              response_headers=__default_response_headers, response_status=200):
        """
        Creates a "responses" callback that checks attributes of the request ("expected_request_*")
        and returns a response with the desired attributes ("response_*").
        Only works for JSON data.
        Parameters
        ----------

        expected_request_body: obj
            the body you expect to be sent with the request
        expected_request_query_params: obj
            the query params you expect to be sent with the request
        response_body: obj
            the body you want the HTTP response to contain
        response_headers: obj
            the headers you want the HTTP response to have
        response_status: int


        Returns
        -------
        a function you can give to the keyword argument "callback" of "responses.add"
        """
        def request_callback(request):
            # check the request query parameters
            if expected_request_query_params:
                self.assertEqual(len(expected_request_query_params), len(request.params))
                for param in request.params:
                    # the 'first' key in request.params will have the URL path before the query string
                    sane_param = param
                    if '?' in param:
                        sane_param = param.split('?')[1]
                    self.assertEqual(request.params[param], expected_request_query_params[sane_param])

            # check the request body
            if expected_request_body is None:
                self.assertEqual(expected_request_body, request.body)
            else:
                self.assertEqual(expected_request_body, json.loads(request.body))

            if response_body is None:
                string_response_body = None
            elif isinstance(response_body, str):
                string_response_body = response_body
            else:
                string_response_body = json.dumps(response_body)
            return (response_status, response_headers, string_response_body)
        return request_callback

    def verify_api_exception(self, exception, expected_status_code, expected_body,
                             expected_headers=__default_response_headers):
        """
        Verifies that an API exception has the fields that would be useful to troubleshooters.
        Parameters
        ----------
        exception: ApiException
            the API exception
        expected_status_code: int
            the HTTP status code expected to be buried in the exception
        expected_body: str
            the response body you expect to be buried in the exception
        expected_headers: dict
            the response headers you expect to be buried in the exception

        Returns
        -------
        None
        """
        self.assertEqual(expected_status_code, exception.response.status_code)
        self.assertEqual(expected_body, exception.response.text)
        self.assertEqual(expected_headers, exception.response.headers)
