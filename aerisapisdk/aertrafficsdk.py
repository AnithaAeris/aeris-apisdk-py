import json
import requests
import aerisapisdk.aerisutils as aerisutils


def getdevicesummaryreport(accountId, apiKey, email, deviceIdType, deviceId):
    endpoint = 'https://aertrafficapi.aeris.com/v1/'
    endpoint = endpoint + accountId
    endpoint = endpoint + '/systemReports/deviceSummary'
    myparams = {'apiKey': apiKey, "durationInMonths": '3', 'subAccounts': 'false'}
    print("Endpoint: " + endpoint)
    print("Params: " + str(myparams))
    r = requests.get(endpoint, params = myparams)
    print("Response code: " + str(r.status_code))
    print(r.text)