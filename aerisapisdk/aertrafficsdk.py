import json
import requests
import aerisapisdk.aerisutils as aerisutils


atbase = 'https://aertrafficapi.aeris.com/'
atv1base = atbase + 'v1/'


def get_endpoint():
    return atv1base

def ping(verbose):
    endpoint = atbase
    r = requests.get(endpoint)
    aerisutils.vprint(verbose, "Response code: " + str(r.status_code))
    if (r.status_code == 200):  # We are expecting a 200 in this case
        print('Endpoint is alive: ' + endpoint)
    elif (r.status_code == 404):
        print('Not expecting a 404 ...')
        aerisutils.print_http_error(r)
    else:
        aerisutils.print_http_error(r)


def getdevicesummaryreport(accountId, apiKey, email, deviceIdType, deviceId):
    endpoint = get_endpoint() + accountId
    endpoint = endpoint + '/systemReports/deviceSummary'
    myparams = {'apiKey': apiKey, "durationInMonths": '3', 'subAccounts': 'false'}
    print("Endpoint: " + endpoint)
    print("Params: " + str(myparams))
    r = requests.get(endpoint, params=myparams)
    print("Response code: " + str(r.status_code))
    print(r.text)
