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
    """Checks that the AerFrame API and AerFrame Longpoll endpoints are reachable.
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


def get_applications(accountId, apiKey, searchAppShortName, verbose=False):
    """Gets a list of all registered applications for the account.

    Parameters
    ----------
    accountId : str
        String version of the numerical account ID
    apiKey : str
        String version of the GUID API Key. Can be found in AerPort / Quicklinks / API Keys
    searchAppShortName : str
        String short name of the application to search for
    verbose : bool, optional
        True to enable verbose printing

    Returns
    -------
    str
        String version of the GUID app ID for the app short name passed in or None if no match found

    Raises
    ------
    ApiException
        if there was a problem

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
    """Gets a specific registered application

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
    dict
        A dictionary containing configuration information for this application

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
    """Creates a registered application

    Parameters
    ----------
    appDescription
    accountId : str
        String version of the numerical account ID
    apiKey : str
        String version of the GUID API Key. Can be found in AerPort / Quicklinks / API Keys
    appShortName : str
        String to use for the short name of the application
    verbose : bool, optional
        True to print verbose output

    Returns
    -------
    dict
        A dict containing configuration information for this application

    Raises
    ------
    ApiException
        in case of an API error.
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
    """Deletes a registered application

    Parameters
    ----------
    accountId : str
        String version of the numerical account ID
    apiKey : str
        String version of the GUID API Key. Can be found in AerPort / Quicklinks / API Keys
    appId : str
        String version of the GUID app ID returned by the create_application call
    verbose : bool, optional
        True to print verbose output; currently unused.

    Returns
    -------
    bool
        True if successfully deleted
        False if the application did not exist

    Raises
    ------
    ApiException
        if there was a problem

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
    """Gets a channel's ID by its application tag. If there are multiple channels with the same application tag, returns
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
    ApiException
        if there was an API problem.

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
    """Gets details of a channel.

    Parameters
    ----------
    accountId: str
    apiKey: str
    channelId: str
    verbose: bool, optional

    Returns
    -------
    dict
        A dict containing the channel configuration details, or None if the channel was not found

    Raises
    ------
    ApiException
        if there was another problem with the API
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
    """Creates a channel

    Parameters
    ----------
    accountId: str
    apiKey: str
    applicationTag: str
        a tag for this channel
    verbose: bool, optional

    Returns
    -------
    dict
        A dict containing the channel configuration.

    Raises
    ------
    ApiException
        if there was a problem
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


def delete_channel(accountId, apiKey, channelId, verbose=False):
    """Deletes a channel.

    Parameters
    ----------
    accountId: str
    apiKey: str
    channelId: str
        the channel ID to delete
    verbose: bool, optional

    Returns
    -------
    bool
        True if the channel was deleted, False if the channel did not exist

    Raises
    ------
    ApiException
        if there was a problem with the API.
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


def get_subscriptions_by_app_short_name(accountId, appApiKey, appShortName, verbose=False):
    """Prints the subscription ID for an inbound and an outbound subscription for the application given by appShortName

    Parameters
    ----------
    accountId: str
        The account ID that owns the application
    appApiKey: str
        The application API key for the application
    appShortName: str
        The short name of the application
    verbose: bool
        True to print verbose output.

    Returns
    -------
    None
    """
    get_inbound_subscription_by_app_short_name(accountId, appApiKey, appShortName, verbose)
    get_outbound_subscription_id_by_app_short_name(accountId, appApiKey, appShortName, verbose)


def get_inbound_subscription_by_app_short_name(accountId, appApiKey, appShortName, verbose=False):
    """
    Prints and returns the subscription ID of the first inbound subscription for the application given by appShortName

    Parameters
    ----------
    accountId: str
        The account ID that owns the application
    appApiKey: str
        The application API key for the application
    appShortName: str
        The short name of the application
    verbose: bool
        True to print verbose output.

    Returns
    -------
    str
       The ID of the first subscription found, or None if no subscriptions were found for the application.

    Raises
    ------
    ApiException
        if there was another problem with the API.
    """
    endpoint = aerisconfig.get_aerframe_api_url() + '/smsmessaging/v2/' + accountId + '/inbound/subscriptions'
    myparams = {'apiKey': appApiKey}
    r = requests.get(endpoint, params=myparams)
    aerisutils.vprint(verbose, "Response code: " + str(r.status_code))
    if r.status_code == 200:
        subscriptions = json.loads(r.text)
        aerisutils.vprint(verbose, json.dumps(subscriptions['subscription'], indent=4))  # Print formatted json
        if 'subscription' not in subscriptions.keys():
            print(f'No inbound subscriptions for application short name {appShortName}')
            return None
        print('Inbound subscriptions:\n')
        for subscription in subscriptions['subscription']:  # Iterate subscriptions to try and find sdk application
            print(subscription['destinationAddress'])
            if appShortName in subscription['destinationAddress']:
                subscription_id = subscription['resourceURL'].split('/')[-1]
                print(appShortName + ' inbound subscription ID: ' + subscription_id)
                return subscription_id
    else:  # Response code was not 200
        aerisutils.print_http_error(r)
        raise ApiException('HTTP status code was: ' + str(r.status_code), r)


def get_outbound_subscription_id_by_app_short_name(accountId, appApiKey, appShortName, verbose=False):
    """Gets the Subscription ID of the first outbound subscription for the application given by appShortName

    Parameters
    ----------
    accountId: str
        The account ID that owns the application
    appApiKey: str
        The application API key for the application
    appShortName: str
        The short name of the application
    verbose: bool
        True to print verbose output.

    Returns
    -------
    str
       The ID of the first subscription found, or None if no subscriptions were found for the application.

    Raises
    ------
    ApiException
        if there was another problem with the API.

    """
    url = aerisconfig.get_aerframe_api_url()
    endpoint = url + '/smsmessaging/v2/' + accountId + '/outbound/' + appShortName + '/subscriptions'
    myparams = {'apiKey': appApiKey}
    r = requests.get(endpoint, params=myparams)
    aerisutils.vprint(verbose, "Response code: " + str(r.status_code))
    if r.status_code == 200:
        subscriptions = json.loads(r.text)
        if 'deliveryReceiptSubscription' in subscriptions.keys():
            aerisutils.vprint(verbose, appShortName + ' has outbound (MT-DR) subscriptions.' + json.dumps(subscriptions,
                                                                                                          indent=4))
            subscriptionId \
                = subscriptions['deliveryReceiptSubscription'][0]['resourceURL'].split('/subscriptions/', 1)[1]
            print(appShortName + ' outbound subscription ID: ' + subscriptionId)
            return subscriptionId
        else:
            print(appShortName + ' has no outbound (MT-DR) subscriptions.')
            return None
    else:  # Response code was not 200
        aerisutils.print_http_error(r)
        raise ApiException('HTTP status code was: ' + str(r.status_code), r)


def get_outbound_subscription(accountId, appApiKey, appShortName, subscriptionId, verbose=False):
    """Gets the details of an outbound subscription, given its subscription ID
    and the short name of the associated application.

    Parameters
    ----------
    accountId: str
        The account ID that owns the application
    appApiKey: str
        The application API key for the application
    appShortName: str
        The short name of the application
    subscriptionId: str
        The ID of the subscription
    verbose: bool, optional
        True to print verbose output.

    Returns
    -------
    dict
        A dict containing details of the subscription, or None if no subscription was found.

    Raises
    ------
    ApiException
        if there was a problem.
    """
    url = aerisconfig.get_aerframe_api_url()
    endpoint = url + '/smsmessaging/v2/' + accountId + '/outbound/' + appShortName + '/subscriptions/' + subscriptionId
    myparams = {'apiKey': appApiKey}
    r = requests.get(endpoint, params=myparams)
    aerisutils.vprint(verbose, "Response code: " + str(r.status_code))
    if r.status_code == 200:
        subscription = json.loads(r.text)
        return subscription
    if r.status_code == 404:
        return None
    else:  # Response code was not 200
        aerisutils.print_http_error(r)
        raise ApiException('HTTP status code was: ' + str(r.status_code), r)


def create_outbound_subscription(accountId, appApiKey, appShortName, appChannelId, verbose=False):
    """Creates an outbound subscription.

    Parameters
    ----------
    accountId: str
        The account ID that owns the application identified by appShortName
    appApiKey: str
        The API key of the application identified by appShortName
    appShortName: str
        The short name of an application
    appChannelId: str
        The ID of a notification channel associated with the application identified by appShortName
    verbose: bool, optional
        True to print verbose output.
    Returns
    -------
    dict
        A dict containing the subscription configuration, including the subscription ID.

    Raises
    ------
    An ApiException if there was a problem.
    """
    url = aerisconfig.get_aerframe_api_url()
    endpoint = url + '/smsmessaging/v2/' + accountId + '/outbound/' + appShortName + '/subscriptions'
    callbackReference = {
        'callbackData': appShortName + '-mt',
        'notifyURL': aerisconfig.get_aerframe_api_url() + '/notificationchannel/v2/'
        + accountId + '/channels/' + appChannelId + '/callback'
    }
    payload = {'callbackReference': callbackReference,
               'filterCriteria': 'SP:*',  # Could use SP:Aeris as example of service profile
               'destinationAddress': [appShortName]}
    myparams = {"apiKey": appApiKey}
    r = requests.post(endpoint, params=myparams, json=payload)
    aerisutils.vprint(verbose, "Response code: " + str(r.status_code))
    if r.status_code == 201:  # In this case, we get a 201 'created' for success
        subscriptionConfig = json.loads(r.text)
        print('Created outbound (MT-DR) subscription for ' + appShortName)
        aerisutils.vprint(verbose, 'Subscription info:\n' + json.dumps(subscriptionConfig, indent=4))
        return subscriptionConfig
    else:
        aerisutils.print_http_error(r)
        raise ApiException('HTTP status code was: ' + str(r.status_code), r)


def delete_outbound_subscription(accountId, appApiKey, appShortName, subscriptionId, verbose=False):
    """Deletes an outbound subscription.

    Parameters
    ----------
    accountId: str
        The account ID that owns the application.
    appApiKey: str
        The API key of the application.
    appShortName: str
        The short name of the application.
    subscriptionId: str
        The ID of the subscription to delete.
    verbose: bool, optional
        True to print verbose output.

    Returns
    -------
    bool, optional
        True if the subscription was deleted, or False if no such subscription was found.

    Raises
    ------
    ApiException
        if there was another problem.
    """
    url = aerisconfig.get_aerframe_api_url()
    endpoint = url + '/smsmessaging/v2/' + accountId + '/outbound/' + appShortName + '/subscriptions/' + subscriptionId
    myparams = {"apiKey": appApiKey}
    r = requests.delete(endpoint, params=myparams)
    if r.status_code == 204:  # Check for 'no content' http response
        print('Subscription successfully deleted.')
        return True
    elif r.status_code == 404:  # Check if no matching subscription ID
        print('Subscription ID does not match current application.')
        return False
    else:
        aerisutils.print_http_error(r)
        raise ApiException('HTTP status code was: ' + str(r.status_code), r)


# ========================================================================


def send_mt_sms(accountId, apiKey, appShortName, imsiDestination, smsText, verbose=False):
    """Sends a Mobile-Terminated Short Message (MT-SM) to a device.

    Parameters
    ----------
    accountId: str
        The account ID that owns the destination device.
    apiKey: str
        An API key for the account.
    appShortName: str
        The application short name.
    imsiDestination: str
        The IMSI of the destination device.
    smsText: str
        The text payload to send to the device.
    verbose: bool, optional
        True to enable verbose printing.

    Returns
    -------
    dict
        A dict containing AerFrame's response, or None if the device was not found or does not support SMS.

    Raises
    ------
    ApiException
        if there was another problem with the API.
    """
    url = aerisconfig.get_aerframe_api_url()
    endpoint = f'{url}/smsmessaging/v2/{accountId}/outbound/{appShortName}/requests'
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
        return None
    else:
        aerisutils.print_http_error(r)
        raise ApiException('HTTP status code was ' + str(r.status_code), r)


def poll_notification_channel(accountId, apiKey, channelURL, verbose=False):
    """
    Polls a notification channel for notifications.

    Parameters
    ----------
    accountId: str
        The account ID that owns the notification channel.
    apiKey: str
        An API key of that account.
    channelURL: str
        The URL of the notification channel to poll. See method ``get_channel`` for details of a notification channel.
    verbose: bool, optional
        True to verbosely print.

    Returns
    -------
    dict
        A dict containing zero or more MT-SM delivery receipts and zero or more MO-SMs.

    Raises
    ------
    ApiException
        if there was a problem.
    """
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
        raise ApiException('HTTP status code was: ' + str(r.status_code), r)


def notifications_flush_search(accountId, apiKey, channelURL, num, search, verbose=True):
    """
    Polls an AerFrame Notification Channel until there are no MT-SM delivery
    receipts remaining, or num polls have completed, whichever happens first.

    Parameters
    ----------
    accountId: str
        The ID of the account that owns the channel.
    apiKey: str
        An API key for the account that owns the channel
    channelURL: str
        The URL of the notification channel to poll. See the 'get_channel' method for details of a notification channel.
    num: int
        The maximum number of polls to issue.
    search: str
        Unused.
    verbose: bool, optional
        True to print all notifications encountered, plus verbose information.
        If set to False, may omit information you wanted printed.
        True by default.

    Returns
    -------
    None
    """
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
    """Gets information about the location of a device.

    Parameters
    ----------
    accountId: str
        The account ID that owns the device.
    apiKey: str
        An API key for the account ID.
    deviceIdType: str
        The type of device ID supplied. Must be 'MSISDN' or 'IMSI'
    deviceId: str
        The device ID.
    verbose: bool, optional
        True to verbosely print output.

    Returns
    -------
    dict
        representing the device's location.

    Raises
    ------
    ApiException
        if there was a problem.
    """
    url = aerisconfig.get_aerframe_api_url()
    endpoint = f'{url}/networkservices/v2/{accountId}/devices/{deviceIdType}/{deviceId}/networkLocation'
    myparams = {'apiKey': apiKey}
    r = requests.get(endpoint, params=myparams)
    aerisutils.vprint(verbose, "Response code: " + str(r.status_code))
    if r.status_code == 200:
        locationInfo = json.loads(r.text)
        return locationInfo
    else:  # Response code was not 200
        aerisutils.print_http_error(r)
        raise ApiException('HTTP status code was ' + str(r.status_code), r)
