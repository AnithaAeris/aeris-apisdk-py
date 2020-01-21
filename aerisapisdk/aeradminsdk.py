import json
import requests
import aerisapisdk.aerisutils as aerisutils


aabase = 'https://aeradminapi.aeris.com/'
aav5base = aabase + 'AerAdmin_WS_5_0/rest/'


def get_endpoint():
    return aav5base

def ping(verbose):
    endpoint = get_endpoint()
    r = requests.get(endpoint)
    aerisutils.vprint(verbose, "Response code: " + str(r.status_code))
    if (r.status_code == 500):  # We are expecting this since we don't have valid parameters
        print('Endpoint is alive: ' + endpoint)
    elif (r.status_code == 404):
        print('Not expecting a 404 ...')
        aerisutils.print_http_error(r)
    else:
        aerisutils.print_http_error(r)


def get_device_details(verbose, accountId, apiKey, email, deviceIdType, deviceId):
    endpoint = get_endpoint() + 'devices/details'
    payload = {"accountID": accountId,
               "email": email,
               deviceIdType: deviceId}
    myparams = {"apiKey": apiKey}
    r = requests.post(endpoint, params=myparams, json=payload)
    aerisutils.vprint(verbose, "Response code: " + str(r.status_code))
    if (r.status_code == 200):
        device_details = json.loads(r.text)
        aerisutils.vprint(verbose, 'Device details:\n' + json.dumps(device_details, indent=4))
        return device_details
    else:
        aerisutils.print_http_error(r)
        return ''


def get_device_network_details(verbose, accountId, apiKey, email, deviceIdType, deviceId):
    endpoint = get_endpoint() + 'devices/network/details'
    payload = {"accountID": accountId,
               "apiKey": apiKey,
               "email": email,
               deviceIdType: deviceId}
    print("Payload: " + str(payload))
    r = requests.get(endpoint, params=payload)
    aerisutils.vprint(verbose, "Response code: " + str(r.status_code))
    if (r.status_code == 200):
        network_details = json.loads(r.text)
        print('Network details:\n' + json.dumps(network_details, indent=4))
        return network_details
    else:
        aerisutils.print_http_error(r)
        return ''
