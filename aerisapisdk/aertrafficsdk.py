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


def get_device_summary_report(accountId, apiKey, email, deviceIdType, deviceId):
    """Prints a device summary report.

    Parameters
    ----------
    accountId: str
    apiKey: str
    email: str
    deviceIdType: str
    deviceId: str

    Returns
    -------
    None
    """
    endpoint = get_endpoint() + accountId
    endpoint = endpoint + '/systemReports/deviceSummary'
    myparams = {'apiKey': apiKey, "durationInMonths": '3', 'subAccounts': 'false'}
    print("Endpoint: " + endpoint)
    print("Params: " + str(myparams))
    r = requests.get(endpoint, params=myparams)
    print("Response code: " + str(r.status_code))
    print(r.text)
