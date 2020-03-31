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


def get_aertraffic_base():
    """
    Returns the base URL of the AerTraffic API (plus a trailing slash) as a string.
    """
    return aerisconfig.get_aertraffic_url() + '/'


def get_endpoint():
    return get_aertraffic_base() + 'v1/'


def ping(verbose=False):
    endpoint = get_aertraffic_base()
    r = requests.get(endpoint)
    aerisutils.vprint(verbose, "Response code: " + str(r.status_code))
    if (r.status_code == 200):  # We are expecting a 200 in this case
        print('Endpoint is alive: ' + endpoint)
    elif (r.status_code == 404):
        print('Not expecting a 404 ...')
        aerisutils.print_http_error(r)
    else:
        aerisutils.print_http_error(r)


def get_device_summary_report(accountId, apiKey, email, deviceIdType, deviceId, verbose=False):
    """Prints a device summary report.

    Parameters
    ----------
    accountId: str
    apiKey: str
    email: str
    deviceIdType: str
    deviceId: str
    verbose: bool

    Returns
    -------
    None
    """
    endpoint = get_endpoint() + accountId
    endpoint = endpoint + '/systemReports/deviceSummary'
    myparams = {'apiKey': apiKey, "durationInMonths": '3', 'subAccounts': 'false'}
    aerisutils.vprint(verbose, "Endpoint: " + endpoint)
    aerisutils.vprint(verbose, "Params: " + str(myparams))
    r = requests.get(endpoint, params=myparams)
    aerisutils.vprint(verbose, "Response code: " + str(r.status_code))
    print(r.text)
