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


class ApiException(Exception):
    """
    Represents an exception with an Aeris API, such as a device not being found or invalid authentication credentials.

    Does not represent transport-layer problems, such as not being able to reach the Aeris APIs.
    The 'response' attribute will have, at least, the following attributes:

    * status_code, to represent the HTTP status code from the response
    * headers, to represent the HTTP headers sent in the response
    * text, to represent the body of the HTTP response
    """
    def __init__(self, message, response, *args, **kwargs):
        super(Exception, self).__init__(message)
        self.message = message
        self.response = response
