import json
import requests
import aerisapisdk.aerisutils as aerisutils
import aerisapisdk.aerisconfig as aerisconfig
from aerisapisdk.exceptions import ApiException


def get_application_endpoint(accountId, appId=None):
    endpoint_base = aerisconfig.get_aerframe_api_url()
    if appId is None:
        return endpoint_base + '/registration/v2/' + accountId + '/applications'
    else:
        return endpoint_base + '/registration/v2/' + accountId + '/applications/' + appId


def get_channel_endpoint(accountId, channelId=None):
    endpoint_base = aerisconfig.get_aerframe_api_url()
    if channelId is None:
        return endpoint_base + '/notificationchannel/v2/' + accountId + '/channels'
    else:
        return endpoint_base + '/notificationchannel/v2/' + accountId + '/channels/' + channelId


def ping(verbose):
    """
    Checks that the AerFrame API and AerFrame Longpoll endpoints are reachable.
    """
    # Check the AerFrame API:
    af_api_endpoint = get_application_endpoint('1')
    r = requests.get(af_api_endpoint)
    aerisutils.vprint(verbose, "Response code: " + str(r.status_code))
    if r.status_code == 401:  # We are expecting this since we don't have valid parameters
        print('Endpoint is alive: ' + af_api_endpoint)
    elif r.status_code == 404:
        print('Not expecting a 404 ...')
        aerisutils.print_http_error(r)
    else:
        aerisutils.print_http_error(r)

    # Check Longpoll:
    af_lp_endpoint = aerisconfig.get_aerframe_longpoll_url()
    r = requests.get(af_lp_endpoint)
    aerisutils.vprint(verbose, "Response code: " + str(r.status_code))
    if r.status_code == 403:  # We are expecting this since we don't have valid parameters
        print('Endpoint is alive: ' + af_lp_endpoint)
    elif r.status_code == 404:
        print('Not expecting a 404 ...')
        aerisutils.print_http_error(r)
    else:
        aerisutils.print_http_error(r)


def get_applications(accountId, apiKey, searchAppShortName, verbose):
    """
    Calls AerFrame API to get a list of all registered applications for the account.

    Parameters
    ----------
    accountId : str
        String version of the numerical account ID
    apiKey : str
        String version of the GUID API Key. Can be found in AerPort / Quicklinks / API Keys
    searchAppShortName : str
        String short name of the application to search for
    verbose : bool
        True to enable verbose printing

    Returns
    -------
    str
        String version of the GUID app ID for the app short name passed in or None if no match found

    Raises
    ------
    ApiException if there was a problem

    """
    endpoint = get_application_endpoint(accountId)  # Get app endpoint based on account ID
    myparams = {'apiKey': apiKey}
    r = requests.get(endpoint, params=myparams)
    aerisutils.vprint(verbose, "Response code: " + str(r.status_code))
    if r.status_code == 200:
        apps = json.loads(r.text)
        aerisutils.vprint(verbose, json.dumps(apps['application'], indent=4))  # Print formatted json
        searchAppShortNameExists = False
        searchAppShortNameId = None
        for app in apps['application']:  # Iterate applications to try and find application we are looking for
            if app['applicationShortName'] == searchAppShortName:
                searchAppShortNameExists = True
                searchAppShortNameId = app['resourceURL'].split('/applications/', 1)[1]
        if searchAppShortNameExists:
            print(searchAppShortName + ' application exists. Application ID: ' + searchAppShortNameId)
            return searchAppShortNameId
        else:
            print(searchAppShortName + ' application does not exist')
            return searchAppShortNameId
    else:  # Response code was not 200
        aerisutils.print_http_error(r)
        raise ApiException('HTTP status code was ' + str(r.status_code), r)


def get_application_by_app_id(accountId, apiKey, appId, verbose=False):
    """
    Calls AerFrame API to get a specific registered application

    Parameters
    ----------
    accountId : str
        String version of the numerical account ID
    apiKey : str
        String version of the GUID API Key. Can be found in AerPort / Quicklinks / API Keys
    appId : str
        String version of the GUID app ID returned by the create_application call
    verbose : bool
        True to enable verbose printing

    Returns
    -------
    Dictionary
        Configuration information for this application

    """
    endpoint = get_application_endpoint(accountId, appId)  # Get app endpoint based on account ID and appID
    myparams = {'apiKey': apiKey}
    r = requests.get(endpoint, params=myparams)
    aerisutils.vprint(verbose, "Response code: " + str(r.status_code))
    if r.status_code == 200:
        appConfig = json.loads(r.text)
        aerisutils.vprint(verbose, json.dumps(appConfig))
        return appConfig
    else:
        aerisutils.print_http_error(r)
        raise ApiException('HTTP status code was ' + str(r.status_code), r)


def create_application(accountId, apiKey, appShortName, appDescription='Application for aerframe sdk', verbose=False):
    """
    Calls AerFrame API to create a registered application

    Parameters
    ----------
    appDescription
    accountId : str
        String version of the numerical account ID
    apiKey : str
        String version of the GUID API Key. Can be found in AerPort / Quicklinks / API Keys
    appShortName : str
        String to use for the short name of the application

    Returns
    -------
    Dictionary
        Configuration information for this application

    Raises
    ------
    ApiException in case of an API error.
    """
    endpoint = get_application_endpoint(accountId)  # Get app endpoint based on account ID
    payload = {'applicationName': appShortName,
               'description': appDescription,
               'applicationShortName': appShortName,
               'applicationTag': appShortName}
    myparams = {"apiKey": apiKey}
    r = requests.post(endpoint, params=myparams, json=payload)
    aerisutils.vprint(verbose, "Response code: " + str(r.status_code))
    if r.status_code == 201:  # Check for 'created' http response
        appConfig = json.loads(r.text)
        print('Created application ' + appShortName)
        aerisutils.vprint(verbose, 'Application info:\n' + json.dumps(appConfig, indent=4))
        return appConfig
    else:
        aerisutils.print_http_error(r)
        raise ApiException('HTTP status code was ' + str(r.status_code), r)


def delete_application(accountId, apiKey, appId, verbose=False):
    """
    Calls AerFrame API to delete a registered application

    Parameters
    ----------
    accountId : str
        String version of the numerical account ID
    apiKey : str
        String version of the GUID API Key. Can be found in AerPort / Quicklinks / API Keys
    appId : str
        String version of the GUID app ID returned by the create_application call

    Returns
    -------
    bool
        True if successfully deleted
        False if the application did not exist
    Raises
    ------
    ApiException if there was a problem

    """
    endpoint = get_application_endpoint(accountId, appId)  # Get app endpoint based on account ID and appID
    myparams = {"apiKey": apiKey}
    r = requests.delete(endpoint, params=myparams)
    if r.status_code == 204:  # Check for 'no content' http response
        print('Application successfully deleted.')
        return True
    elif r.status_code == 404:  # Check if no matching app ID
        print('Application ID does not match current application.')
        return False
    else:
        aerisutils.print_http_error(r)
        raise ApiException('HTTP status code was ' + str(r.status_code), r)


# ========================================================================


def get_channel_id_by_tag(accountId, apiKey, searchAppTag, verbose=False):
    """
    Gets a channel's ID by its application tag. If there are multiple channels with the same application tag, returns
    only one of them.
    Parameters
    ----------
    accountId: str
    apiKey: str
    searchAppTag: str
        the application tag that the channel was created with
    verbose: bool

    Returns
    -------
    str
        The ID of a channel that has the same application tag as "searchAppTag", or None if none were found

    Raises
    ------
    ApiException if there was an API problem.

    """
    endpoint = get_channel_endpoint(accountId)
    myparams = {'apiKey': apiKey}
    r = requests.get(endpoint, params=myparams)
    aerisutils.vprint(verbose, "Response code: " + str(r.status_code))
    if r.status_code == 200:
        channels = json.loads(r.text)
        aerisutils.vprint(verbose, json.dumps(channels['notificationChannel'], indent=4))  # Print formatted json
        searchAppTagExists = False
        searchAppTagId = None
        sdkchannel = None
        for channel in channels['notificationChannel']:  # Iterate channels to try and find sdk application
            if channel['applicationTag'] == searchAppTag:
                searchAppTagExists = True
                sdkchannel = channel
                searchAppTagId = channel['resourceURL'].split('/channels/', 1)[1]
        if searchAppTagExists:
            print(searchAppTag + ' channel exists. Channel ID: ' + searchAppTagId)
            aerisutils.vprint(verbose, 'Channel config: ' + json.dumps(sdkchannel, indent=4))
            return searchAppTagId
        else:
            print(searchAppTag + ' channel does not exist')
            return searchAppTagId
    else:  # Response code was not 200
        aerisutils.print_http_error(r)
        raise ApiException('HTTP status code was ' + str(r.status_code), r)


def get_channel(accountId, apiKey, channelId, verbose=False):
    """
    Gets details of a channel.
    Parameters
    ----------
    accountId
    apiKey
    channelId
    verbose

    Returns
    -------
    object
        the channel configuration details, or None if the channel was not found

    Raises
    ------
    ApiException if there was another problem with the API
    """
    endpoint = get_channel_endpoint(accountId, channelId)
    myparams = {'apiKey': apiKey}
    r = requests.get(endpoint, params=myparams)
    aerisutils.vprint(verbose, "Response code: " + str(r.status_code))
    if r.status_code == 200:
        channelConfig = json.loads(r.text)
        aerisutils.vprint(verbose, json.dumps(channelConfig))
        return channelConfig
    elif r.status_code == 404:
        aerisutils.print_http_error(r)
        return None
    else:
        aerisutils.print_http_error(r)
        raise ApiException('HTTP status code was ' + str(r.status_code), r)


def create_channel(accountId, apiKey, applicationTag, verbose=False):
    """
    Creates a channel
    Parameters
    ----------
    accountId: str
    apiKey: str
    applicationTag: str
        a tag for this channel
    verbose

    Returns
    -------
    object
        the channel configuration

    Raises
    ------
    ApiException if there was a problem
    """
    endpoint = get_channel_endpoint(accountId)
    channelData = {'maxNotifications': '15',
                   'type': 'nc:LongPollingData'}
    payload = {'applicationTag': applicationTag,
               'channelData': channelData,
               'channelType': 'LongPolling'}
    myparams = {"apiKey": apiKey}
    r = requests.post(endpoint, params=myparams, json=payload)
    aerisutils.vprint(verbose, "Response code: " + str(r.status_code))
    if r.status_code == 200:  # In this case, we get a 200 for success rather than 201 like for application
        channelConfig = json.loads(r.text)
        print('Created notification channel for ' + applicationTag)
        aerisutils.vprint(verbose, 'Notification channel info:\n' + json.dumps(channelConfig, indent=4))
        return channelConfig
    else:
        aerisutils.print_http_error(r)
        raise ApiException('HTTP status code was ' + str(r.status_code), r)


def delete_channel(accountId, apiKey, channelId, verbose):
    """
    Deletes a channel.
    Parameters
    ----------
    accountId: str
    apiKey: str
    channelId: str
        the channel ID to delete
    verbose

    Returns
    -------
    True if the channel was deleted, False if the channel did not exist

    Raises
    ------
    ApiException if there was a problem with the API.
    """
    endpoint = get_channel_endpoint(accountId, channelId)
    myparams = {"apiKey": apiKey}
    r = requests.delete(endpoint, params=myparams)
    if r.status_code == 204:  # Check for 'no content' http response
        print('Channel successfully deleted.')
        return True
    elif r.status_code == 404:  # Check if no matching channel ID
        print('Channel ID does not match current application.')
        return False
    else:
        aerisutils.print_http_error(r)
        raise ApiException('HTTP status code was ' + str(r.status_code), r)


# ========================================================================


def get_subscriptions(accountId, apiKey, appShortName, verbose=False):
    get_inbound_subscriptions(accountId, apiKey, appShortName, verbose)
    get_outbound_subscriptions(accountId, apiKey, appShortName, verbose)


def get_inbound_subscriptions(accountId, apiKey, appShortName, verbose=False):
    endpoint = aerisconfig.get_aerframe_api_url() + '/smsmessaging/v2/' + accountId + '/inbound/subscriptions'
    myparams = {'apiKey': apiKey}
    r = requests.get(endpoint, params=myparams)
    aerisutils.vprint(verbose, "Response code: " + str(r.status_code))
    if r.status_code == 200:
        subscriptions = json.loads(r.text)
        aerisutils.vprint(verbose, json.dumps(subscriptions['subscription'], indent=4))  # Print formatted json
        print('Inbound subscriptions:\n')
        for subscription in subscriptions['subscription']:  # Iterate subscriptions to try and find sdk application
            print(subscription['destinationAddress'])
    else:  # Response code was not 200
        aerisutils.print_http_error(r)
        return ''


def get_outbound_subscriptions(accountId, apiKey, appShortName, verbose=False):
    endpoint = aerisconfig.get_aerframe_api_url() + '/smsmessaging/v2/' + accountId + '/outbound/' \
               + appShortName + '/subscriptions'
    myparams = {'apiKey': apiKey}
    r = requests.get(endpoint, params=myparams)
    aerisutils.vprint(verbose, "Response code: " + str(r.status_code))
    if r.status_code == 200:
        subscriptions = json.loads(r.text)
        if 'deliveryReceiptSubscription' in subscriptions.keys():
            aerisutils.vprint(verbose, appShortName + ' has outbound (MT-DR) subscriptions.' + json.dumps(subscriptions,
                                                                                                          indent=4))
            subscriptionId \
                = subscriptions['deliveryReceiptSubscription'][0]['resourceURL'].split('/subscriptions/', 1)[1]
            print(appShortName + ' subscription ID: ' + subscriptionId)
            return subscriptionId
        else:
            print(appShortName + ' has no outbound (MT-DR) subscriptions.')
            return None
    else:  # Response code was not 200
        aerisutils.print_http_error(r)
        return None


def get_outbound_subscription(accountId, apiKey, appShortName, subscriptionId, verbose=False):
    endpoint = aerisconfig.get_aerframe_api_url() + '/smsmessaging/v2/' + accountId + '/outbound/' \
               + appShortName + '/subscriptions/' + subscriptionId
    myparams = {'apiKey': apiKey}
    r = requests.get(endpoint, params=myparams)
    aerisutils.vprint(verbose, "Response code: " + str(r.status_code))
    if r.status_code == 200:
        subscription = json.loads(r.text)
        return subscription
    else:  # Response code was not 200
        aerisutils.print_http_error(r)
        return ''


def create_outbound_subscription(accountId, apiKey, appShortName, appChannelId, verbose=False):
    endpoint = aerisconfig.get_aerframe_api_url() + '/smsmessaging/v2/' + accountId + '/outbound/' \
               + appShortName + '/subscriptions'
    callbackReference = {
        'callbackData': appShortName + '-mt',
        'notifyURL': aerisconfig.get_aerframe_api_url() + '/notificationchannel/v2/'
        + accountId + '/channels/' + appChannelId + '/callback'
    }
    payload = {'callbackReference': callbackReference,
               'filterCriteria': 'SP:*',  # Could use SP:Aeris as example of service profile
               'destinationAddress': [appShortName]}
    myparams = {"apiKey": apiKey}
    r = requests.post(endpoint, params=myparams, json=payload)
    aerisutils.vprint(verbose, "Response code: " + str(r.status_code))
    if r.status_code == 201:  # In this case, we get a 201 'created' for success
        subscriptionConfig = json.loads(r.text)
        print('Created outbound (MT-DR) subscription for ' + appShortName)
        aerisutils.vprint(verbose, 'Subscription info:\n' + json.dumps(subscriptionConfig, indent=4))
        return subscriptionConfig
    else:
        aerisutils.print_http_error(r)
        return None


def delete_outbound_subscription(accountId, apiKey, appShortName, subscriptionId, verbose=False):
    endpoint = aerisconfig.get_aerframe_api_url() + '/smsmessaging/v2/' + accountId + '/outbound/' \
               + appShortName + '/subscriptions/' + subscriptionId
    myparams = {"apiKey": apiKey}
    r = requests.delete(endpoint, params=myparams)
    if r.status_code == 204:  # Check for 'no content' http response
        print('Subscription successfully deleted.')
        return True
    elif r.status_code == 404:  # Check if no matching subscription ID
        print('Subscription ID does not match current application.')
        return False
    else:
        aerisutils.print_http_error(r)
        return False


# ========================================================================


def send_mt_sms(accountId, apiKey, appShortName, imsiDestination, smsText, verbose=False):
    endpoint = aerisconfig.get_aerframe_api_url() \
               + '/smsmessaging/v2/' + accountId + '/outbound/' + appShortName + '/requests'
    address = [imsiDestination]
    outboundSMSTextMessage = {"message": smsText}
    payload = {'address': address,
               'senderAddress': appShortName,
               'outboundSMSTextMessage': outboundSMSTextMessage,
               'clientCorrelator': '123456',
               'senderName': appShortName}
    myparams = {"apiKey": apiKey}
    # print('Payload: \n' + json.dumps(payload, indent=4))
    r = requests.post(endpoint, params=myparams, json=payload)
    aerisutils.vprint(verbose, "Response code: " + str(r.status_code))
    if r.status_code == 201:  # In this case, we get a 201 'created' for success
        sendsmsresponse = json.loads(r.text)
        print('Sent SMS:\n' + json.dumps(sendsmsresponse, indent=4))
        return sendsmsresponse
    elif r.status_code == 404:  # Check if no matching device IMSI or IMSI not support SMS
        print('IMSI is not found or does not support SMS.')
        print(r.text)
        return False
    else:
        aerisutils.print_http_error(r)
        return ''


def poll_notification_channel(accountId, apiKey, channelURL, verbose=False):
    myparams = {'apiKey': apiKey}
    print('Polling channelURL for polling interval: ' + channelURL)
    r = requests.get(channelURL, params=myparams)
    aerisutils.vprint(verbose, "Response code: " + str(r.status_code))
    if r.status_code == 200:
        notifications = json.loads(r.text)
        aerisutils.vprint(verbose, 'MO SMS and MT SMS DR:\n' + json.dumps(notifications, indent=4))
        return notifications
    else:  # Response code was not 200
        aerisutils.print_http_error(r)
        return None


def notifications_flush_search(accountId, apiKey, channelURL, num, search, verbose=False):
    print('Polling channelURL for polling interval: ' + channelURL)
    for x in range(num):  # Poll up to num times
        notifications = poll_notification_channel(accountId, apiKey, channelURL, verbose)
        if notifications is not None:
            if len(notifications['deliveryInfoNotification']) == 0:
                print('No pending notifications')
                return None
            else:
                num_notifications = len(notifications['deliveryInfoNotification'][0]['deliveryInfo'])
                print('Number of notifications = ' + str(num_notifications))


def get_location(accountId, apiKey, deviceIdType, deviceId, verbose=False):
    endpoint = aerisconfig.get_aerframe_api_url() + '/networkservices/v2/' + accountId + '/devices/' \
               + deviceIdType + '/' + deviceId + '/networkLocation'
    myparams = {'apiKey': apiKey}
    r = requests.get(endpoint, params=myparams)
    aerisutils.vprint(verbose, "Response code: " + str(r.status_code))
    if r.status_code == 200:
        locationInfo = json.loads(r.text)
        print('Location information:\n' + json.dumps(locationInfo, indent=4))
        return locationInfo
    else:  # Response code was not 200
        aerisutils.print_http_error(r)
        raise ApiException('HTTP status code was ' + str(r.status_code), r)
