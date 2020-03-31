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
import requests
import aerisapisdk.aerisutils as aerisutils
import aerisapisdk.aerisconfig as aerisconfig
from aerisapisdk.exceptions import ApiException


def get_aeradmin_base():
    """Returns the AerAdmin API base URL plus a trailing slash as a string.
    """
    return aerisconfig.get_aeradmin_url() + '/'


def get_endpoint():
    return get_aeradmin_base() + 'AerAdmin_WS_5_0/rest/'


def ping(verbose):
    endpoint = get_endpoint()
    r = requests.get(endpoint)
    aerisutils.vprint(verbose, "Response code: " + str(r.status_code))
    if r.status_code == 500:  # We are expecting this since we don't have valid parameters
        print('Endpoint is alive: ' + endpoint)
    elif r.status_code == 404:
        print('Not expecting a 404 ...')
        aerisutils.print_http_error(r)
    else:
        aerisutils.print_http_error(r)


def get_device_details(accountId, apiKey, email, deviceIdType, deviceId, verbose=False):
    """Gets and prints details for a device.
    Parameters
    ----------
    accountId: str
        The account ID that owns the device
    apiKey: str
        An API Key for the account ID
    email: str
        The email address of the user making this request
    deviceIdType: str
        The type of device ID to query. See
        https://aeriscom.zendesk.com/hc/en-us/articles/360037274334-AerAdmin-5-0-REST-API-Specification for possible
        values.
    deviceId: str
        The ID of the device to query
    verbose: bool, optional
        True if you want extra output printed

    Returns
    -------
    dict
        A dict representing the device's details.

    Raises
    ------
    ApiException
        if there was a problem.
    """
    endpoint = get_endpoint() + 'devices/details'
    payload = {"accountID": accountId,
               "email": email,
               deviceIdType: deviceId}
    myparams = {"apiKey": apiKey}
    r = requests.post(endpoint, params=myparams, json=payload)
    aerisutils.vprint(verbose, "Response code: " + str(r.status_code))
    if r.status_code == 200:
        device_details = json.loads(r.text)
        print('Device details:\n' + json.dumps(device_details, indent=4))
        result_code = None
        if 'resultCode' in device_details:
            result_code = device_details['resultCode']
        if result_code == 0:
            return device_details

        raise ApiException('Bad (or missing) resultCode: ' + str(result_code), r)
    else:
        aerisutils.print_http_error(r)
        raise ApiException('HTTP status code was not 200', r)


def get_device_network_details(accountId, apiKey, email, deviceIdType, deviceId, verbose=False):
    """Gets and prints details about a device's network attributes (e.g., last registration time)
    Parameters
    ----------
    accountId: str
    apiKey: str
    email: str
    deviceIdType: str
        The type of device ID to query. See
        https://aeriscom.zendesk.com/hc/en-us/articles/360037274334-AerAdmin-5-0-REST-API-Specification for possible
        values.
    deviceId: str
    verbose: bool, optional

    Returns
    -------
    dict
        A dict representing the network details of the device.

    Raises
    ------
    ApiException
        if there was a problem with the API.
    """
    endpoint = get_endpoint() + 'devices/network/details'
    payload = {"accountID": accountId,
               "apiKey": apiKey,
               "email": email,
               deviceIdType: deviceId}
    aerisutils.vprint(verbose, "Payload: " + str(payload))
    r = requests.get(endpoint, params=payload)
    aerisutils.vprint(verbose, "Response code: " + str(r.status_code))
    if r.status_code == 200:
        network_details = json.loads(r.text)
        print('Network details:\n' + json.dumps(network_details, indent=4))
        result_code = None
        if 'resultCode' in network_details:
            result_code = network_details['resultCode']
        if result_code == 0:
            return network_details
        raise ApiException('Bad (or missing) resultCode: ' + str(result_code), r)
    else:
        aerisutils.print_http_error(r)
        raise ApiException('HTTP status code was not 200', r)
