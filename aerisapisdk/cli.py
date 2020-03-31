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

import click
import json
import pathlib
import aerisapisdk.aeradminsdk as aeradminsdk
import aerisapisdk.aertrafficsdk as aertrafficsdk
import aerisapisdk.aerframesdk as aerframesdk
import aerisapisdk.aerisutils as aerisutils
import aerisapisdk.aerisconfig as aerisconfig


default_config_filename = aerisconfig.default_config_filename
afsdkappname = 'aerframesdk'  # Short name used for the AerFrame application created for this SDK


# Loads configuration from file
def load_config(ctx, config_filename):
    try:
        ctx.obj.update(aerisconfig.load_config(config_filename))
        aerisutils.vprint(ctx.obj['verbose'], 'Configuration: ' + str(ctx.obj))
        return True
    except IOError:
        return False


# Allows us to set the default option value based on value in the context
def default_from_context(default_name, default_value=' '):
    class OptionDefaultFromContext(click.Option):
        def get_default(self, ctx):
            try:
                self.default = ctx.obj[default_name]
            except KeyError:
                self.default = default_value
            return super(OptionDefaultFromContext, self).get_default(ctx)

    return OptionDefaultFromContext


def default_option_from_context_hierarchy(default_value=None, *names):
    """Allows us to set a default option value based on some path into the context.

    Parameters
    ----------
    default_value
        The default value to return if no suitable value is found in the context
    names: list
        The keys to look up in the context for the default value

    Returns
    -------
    The default option value.
    """
    class OptionDefaultFromContext(click.Option):
        def get_default(self, ctx):
            try:
                current_value = ctx.obj[names[0]]
                for name in names[1:]:
                    current_value = current_value[name]
                self.default = current_value
            except KeyError:
                self.default = default_value
            return super(OptionDefaultFromContext, self).get_default(ctx)
    return OptionDefaultFromContext
#
#
# Define the main highest-level group of commands
#
#
@click.group()
@click.option('-v', '--verbose', is_flag=True, default=False, help="Verbose output")
@click.option("--config-file", "-cfg", default=default_config_filename,
              help="Path to config file.")
@click.pass_context
def mycli(ctx, verbose, config_file):
    ctx.obj['verbose'] = verbose
    print('context:\n' + str(ctx.invoked_subcommand))
    if load_config(ctx, config_file):
        aerisutils.vprint(verbose, 'Valid config for account ID: ' + ctx.obj['accountId'])
    elif ctx.invoked_subcommand not in ['config',
                                        'ping']:  # This is not ok unless we are doing a config or ping command
        print('Valid configuration not found')
        print('Try running config command')
        exit()
    # else: We are doing a config command


@mycli.command()
@click.pass_context
def ping(ctx):
    """Simple ping of the api endpoints
    \f

    """
    print('Checking all api endpoints ...')
    aeradminsdk.ping(ctx.obj['verbose'])
    aertrafficsdk.ping(ctx.obj['verbose'])
    aerframesdk.ping(ctx.obj['verbose'])


@mycli.command()
@click.option('--accountid', prompt='Account ID', cls=default_from_context('accountId'), help="Customer account ID.")
@click.option('--apikey', prompt='API Key', cls=default_from_context('apiKey'), help="Customer API key.")
@click.option('--email', prompt='Email address', cls=default_from_context('email'), help="User email address.")
@click.option('--deviceidtype', prompt='Device ID type', type=click.Choice(['ICCID', 'IMSI']),
              cls=default_from_context('primaryDeviceIdType', 'ICCID'), help="Device identifier type.")
@click.option('--deviceid', prompt='Device ID', cls=default_from_context('primaryDeviceId'), help="Device ID.")
@click.pass_context
def config(ctx, accountid, apikey, email, deviceidtype, deviceid):
    """Set up the configuration for using this tool
    \f

    """
    config_values = {"accountId": accountid,
                     "apiKey": apikey,
                     "email": email,
                     "primaryDeviceIdType": deviceidtype,
                     "primaryDeviceId": deviceid}
    with open(default_config_filename, 'w') as myconfigfile:
        try:
            _set_config_file_permissions(default_config_filename)
        except BaseException as e:
            print(f'WARNING: Could not set permissions for file {default_config_filename}. Reason: {e}')
            print('WARNING: You should ensure that the permissions of the file keep your API key secret.')
        json.dump(config_values, myconfigfile, indent=4)


def _set_config_file_permissions(filename):
    """
    Sets the permissions of the configuration file such that only the current user can read or write the file.

    Parameters
    ----------
    filename: str

    Returns
    -------
    None
    """
    import platform
    if platform.system() == 'Windows':
        # hat tip to http://timgolden.me.uk/python/win32_how_do_i/add-security-to-a-file.html
        import win32security
        import win32api
        import ntsecuritycon as con
        user, domain, type = win32security.LookupAccountName("", win32api.GetUserName())
        system_user, domain, type = win32security.LookupAccountName("", 'SYSTEM')
        security_descriptor = win32security.GetFileSecurity(filename, win32security.DACL_SECURITY_INFORMATION)
        dacl_to_set = win32security.ACL()
        # ensure that SYSTEM still has full access --
        # https://docs.microsoft.com/en-us/windows/security/identity-protection/access-control/local-accounts says
        # "The SYSTEM account's permissions can be removed from a file, but we do not recommend removing them."
        dacl_to_set.AddAccessAllowedAce(win32security.ACL_REVISION, con.FILE_ALL_ACCESS, system_user)
        # The current user is the only normal user that should have access:
        dacl_to_set.AddAccessAllowedAce(win32security.ACL_REVISION,
                                        con.FILE_GENERIC_READ | con.FILE_GENERIC_WRITE, user)
        security_descriptor.SetSecurityDescriptorDacl(1, dacl_to_set, 0)
        win32security.SetFileSecurity(filename, win32security.DACL_SECURITY_INFORMATION, security_descriptor)
    else:
        import os
        import stat
        os.chmod(filename, stat.S_IRUSR | stat.S_IWUSR)


# ========================================================================
#
# Define the aeradmin group of commands
#
@mycli.group()
@click.pass_context
def aeradmin(ctx):
    """AerAdmin API Services
    \f

    """


@aeradmin.command()  # Subcommand: aeradmin device
@click.pass_context
def device(ctx):
    """AerAdmin get device details
    \f

    """
    aeradminsdk.get_device_details(ctx.obj['accountId'], ctx.obj['apiKey'], ctx.obj['email'],
                                   ctx.obj['primaryDeviceIdType'], ctx.obj['primaryDeviceId'], ctx.obj['verbose'])


@aeradmin.command()  # Subcommand: aeradmin network
@click.pass_context
def network(ctx):
    """AerAdmin get device network details
    \f

    """
    aeradminsdk.get_device_network_details(ctx.obj['accountId'], ctx.obj['apiKey'], ctx.obj['email'],
                                           ctx.obj['primaryDeviceIdType'], ctx.obj['primaryDeviceId'],
                                           ctx.obj['verbose'])


# ========================================================================
#
# Define the aertraffic group of commands
#
@mycli.group()
@click.pass_context
def aertraffic(ctx):
    """AerTraffic API Services
    \f

    """


@aertraffic.command()  # Subcommand: aertraffic devicesummaryreport
@click.pass_context
def devicesummaryreport(ctx):
    aertrafficsdk.get_device_summary_report(ctx.obj['accountId'], ctx.obj['apiKey'], ctx.obj['email'],
                                            ctx.obj['primaryDeviceIdType'], ctx.obj['primaryDeviceId'],
                                            ctx.obj['verbose'])


# ========================================================================
#
# Define the aerframe group of commands
#
@mycli.group()
@click.pass_context
def aerframe(ctx):
    """AerFrame API Services
    \f

    """


@aerframe.command()  # Subcommand: aerframe init
@click.pass_context
def init(ctx):
    """Initialize application, notification channel, and subscription
    \f

    """
    # AerFrame application
    aerframeApplicationId = aerframesdk.get_applications(ctx.obj['accountId'], ctx.obj['apiKey'], afsdkappname,
                                                         ctx.obj['verbose'])
    if aerframeApplicationId is None:
        aerframeApplication = aerframesdk.create_application(ctx.obj['accountId'], ctx.obj['apiKey'], afsdkappname,
                                                             verbose=ctx.obj['verbose'])
    else:
        aerframeApplication = aerframesdk.get_application_by_app_id(ctx.obj['accountId'], ctx.obj['apiKey'],
                                                                    aerframeApplicationId, ctx.obj['verbose'])
    ctx.obj['aerframeApplication'] = aerframeApplication
    # Notification channel
    aerframeChannelId = aerframesdk.get_channel_id_by_tag(ctx.obj['accountId'], ctx.obj['apiKey'], afsdkappname,
                                                          ctx.obj['verbose'])
    if aerframeChannelId is None:
        aerframeChannel = aerframesdk.create_channel(ctx.obj['accountId'], ctx.obj['apiKey'], afsdkappname,
                                                     ctx.obj['verbose'])
    else:
        aerframeChannel = aerframesdk.get_channel(ctx.obj['accountId'], ctx.obj['apiKey'], aerframeChannelId,
                                                  ctx.obj['verbose'])
    ctx.obj['aerframeChannel'] = aerframeChannel
    # Subscription
    appApiKey = ctx.obj['aerframeApplication']['apiKey']
    aerframeSubscriptionId = aerframesdk.get_outbound_subscription_id_by_app_short_name(ctx.obj['accountId'], appApiKey,
                                                                                        afsdkappname,
                                                                                        ctx.obj['verbose'])
    if aerframeSubscriptionId is None:
        afchid = ctx.obj['aerframeChannel']['resourceURL'].split('/channels/', 1)[1]
        aerframeSubscription = aerframesdk.create_outbound_subscription(ctx.obj['accountId'], appApiKey, afsdkappname,
                                                                        afchid, ctx.obj['verbose'])
    else:
        aerframeSubscription = aerframesdk.get_outbound_subscription(ctx.obj['accountId'], appApiKey, afsdkappname,
                                                                     aerframeSubscriptionId, ctx.obj['verbose'])
    ctx.obj['aerframeSubscription'] = aerframeSubscription
    aerisutils.vprint(ctx.obj['verbose'], '\nUpdated aerframe subscription config: ' + str(ctx.obj))
    # Device IDs
    deviceDetails = aeradminsdk.get_device_details(ctx.obj['accountId'], ctx.obj['apiKey'], ctx.obj['email'],
                                                   ctx.obj['primaryDeviceIdType'], ctx.obj['primaryDeviceId'],
                                                   ctx.obj['verbose'])
    ctx.obj['deviceId'] = deviceDetails['deviceAttributes'][0]['deviceID']
    # Write all this to our config file
    with open(default_config_filename, 'w') as myconfigfile:
        ctx.obj.pop('verbose', None)  # Don't store the verbose flag
        json.dump(ctx.obj, myconfigfile, indent=4)


@aerframe.command()  # Subcommand: aerframe reset
@click.pass_context
def reset(ctx):
    """Clear application, notification channel, and subscription
    \f

    """
    # Subscription
    appApiKey = ctx.obj['aerframeApplication']['apiKey']
    aerframeSubscriptionId = aerframesdk.get_outbound_subscription_id_by_app_short_name(ctx.obj['accountId'], appApiKey,
                                                                                        afsdkappname,
                                                                                        ctx.obj['verbose'])
    if aerframeSubscriptionId is not None:
        aerframesdk.delete_outbound_subscription(ctx.obj['accountId'], ctx.obj['aerframeApplication']['apiKey'],
                                                 afsdkappname, aerframeSubscriptionId, ctx.obj['verbose'])
        # Notification channel
    aerframeChannelId = aerframesdk.get_channel_id_by_tag(ctx.obj['accountId'], ctx.obj['apiKey'], afsdkappname,
                                                          ctx.obj['verbose'])
    if aerframeChannelId is not None:
        aerframesdk.delete_channel(ctx.obj['accountId'], ctx.obj['apiKey'], aerframeChannelId, ctx.obj['verbose'])
        # AerFrame application
    aerframeApplicationId = aerframesdk.get_applications(ctx.obj['accountId'], ctx.obj['apiKey'], afsdkappname,
                                                         ctx.obj['verbose'])
    if aerframeApplicationId is not None:
        aerframesdk.delete_application(ctx.obj['accountId'], ctx.obj['apiKey'], aerframeApplicationId,
                                       ctx.obj['verbose'])


@aerframe.group()
@click.pass_context
def application(ctx):  # Subcommand: aerframe application
    """AerFrame application commands
    \f

    """


@application.command()  # Subcommand: aerframe application get
@click.option('--aps', default=afsdkappname, help="Application short name to find")
@click.pass_context
def get(ctx, aps):
    """Get AerFrame applications
    \f

    """
    afappid = aerframesdk.get_applications(ctx.obj['accountId'], ctx.obj['apiKey'], aps, ctx.obj['verbose'])
    if afappid is not None:
        afappconfig = aerframesdk.get_application_by_app_id(ctx.obj['accountId'], ctx.obj['apiKey'], afappid,
                                                            ctx.obj['verbose'])
        print('\nApp config: \n' + str(afappconfig))


@application.command()  # Subcommand: aerframe application create
@click.option('--aps', default=afsdkappname, help="Application short name to create")
@click.pass_context
def create(ctx, aps):
    """Create a new AerFrame application
    \f

    """
    aerframesdk.create_application(ctx.obj['accountId'], ctx.obj['apiKey'], aps, verbose=ctx.obj['verbose'])


@application.command()  # Subcommand: aerframe application delete
@click.option('--aps', default=afsdkappname, help="Application short name to delete")
@click.pass_context
def delete(ctx, aps):
    """Delete an AerFrame application
    \f

    """
    afappid = aerframesdk.get_applications(ctx.obj['accountId'], ctx.obj['apiKey'], aps, ctx.obj['verbose'])
    if afappid is not None:
        click.confirm('Do you want to delete the app ' + aps + '?', abort=True)
        aerframesdk.delete_application(ctx.obj['accountId'], ctx.obj['apiKey'], afappid, ctx.obj['verbose'])


@aerframe.group()  # Subcommand group: aerframe channel
@click.pass_context
def channel(ctx):
    """AerFrame notification channel commands
    \f

    """


@channel.command()  # Subcommand: aerframe channel get
@click.pass_context
def get(ctx):
    """Get AerFrame notification channels
    \f

    """
    appChannelID = aerframesdk.get_channel_id_by_tag(ctx.obj['accountId'], ctx.obj['apiKey'], afsdkappname,
                                                     ctx.obj['verbose'])
    aerframesdk.get_channel(ctx.obj['accountId'], ctx.obj['apiKey'], appChannelID, ctx.obj['verbose'])


@channel.command()  # Subcommand: aerframe create_channel
@click.pass_context
def create(ctx):
    """Create AerFrame notification channel
    \f

    """
    aerframesdk.create_channel(ctx.obj['accountId'], ctx.obj['apiKey'], 'aerframesdk', ctx.obj['verbose'])


@channel.command()  # Subcommand: aerframe channel delete
@click.pass_context
def delete(ctx):
    """Delete AerFrame notification channel
    \f

    """
    afchannelid = aerframesdk.get_channel_id_by_tag(ctx.obj['accountId'], ctx.obj['apiKey'], afsdkappname,
                                                    ctx.obj['verbose'])
    if afchannelid is not None:
        click.confirm('Do you want to delete the sdk channel?', abort=True)
        aerframesdk.delete_channel(ctx.obj['accountId'], ctx.obj['apiKey'], afchannelid, ctx.obj['verbose'])


@aerframe.group()
@click.pass_context
def subscription(ctx):
    """AerFrame subscription commands
    \f

    """


@subscription.command()  # Subcommand: aerframe subscription get
@click.pass_context
def get(ctx):
    """Get AerFrame subscriptions
    \f

    """
    aerframesdk.get_subscriptions_by_app_short_name(ctx.obj['accountId'], ctx.obj['aerframeApplication']['apiKey'],
                                                    afsdkappname, ctx.obj['verbose'])


@subscription.command()  # Subcommand: aerframe subscription create
@click.pass_context
def create(ctx):
    """Create AerFrame subscription
    \f

    """
    appChannelID = aerframesdk.get_channel_id_by_tag(ctx.obj['accountId'], ctx.obj['apiKey'], afsdkappname,
                                                     ctx.obj['verbose'])
    aerframesdk.create_outbound_subscription(ctx.obj['accountId'], ctx.obj['aerframeApplication']['apiKey'],
                                             afsdkappname, appChannelID, ctx.obj['verbose'])


@subscription.command()  # Subcommand: aerframe subscription delete
@click.pass_context
def delete(ctx):
    """Delete AerFrame subscription
    \f

    """
    afsubid = aerframesdk.get_outbound_subscription_id_by_app_short_name(ctx.obj['accountId'],
                                                                         ctx.obj['aerframeApplication']['apiKey'],
                                                                         afsdkappname, ctx.obj['verbose'])
    if afsubid is not None:
        click.confirm('Do you want to delete the sdk subscription?', abort=True)
        aerframesdk.delete_outbound_subscription(ctx.obj['accountId'], ctx.obj['aerframeApplication']['apiKey'],
                                                 afsdkappname, afsubid, ctx.obj['verbose'])


@aerframe.group()
@click.pass_context
def sms(ctx):
    """AerFrame SMS commands
    \f

    """
    aerisutils.vprint(ctx, 'AerFrame sms commands')


@sms.command()  # Subcommand: aerframe sms send
@click.argument('message', default='Test from aerframesdk.')
@click.option('--imsi', 'imsi', cls=default_option_from_context_hierarchy('', 'deviceId', 'imsi'),
              required=False,
              help='The IMSI of the device to send the SMS. The default is the device used for the "config"'
              + ' and "aerframe init" commands.')
@click.pass_context
def send(ctx, message, imsi):
    """Send MESSAGE as the payload of an SMS to a device.

    If omitted, MESSAGE will be "Test from aerframesdk.".
    \f
    """
    aerframesdk.send_mt_sms(ctx.obj['accountId'], ctx.obj['aerframeApplication']['apiKey'], afsdkappname,
                            imsi, message, ctx.obj['verbose'])


@sms.command()  # Subcommand: aerframe sms receive
@click.option('--num', default=1, help="Number of receive requests")
@click.pass_context
def receive(ctx, num):
    """Receive SMS or Delivery Receipt
    \f

    """
    channelURL = ctx.obj['aerframeChannel']['channelData']['channelURL']
    aerframesdk.notifications_flush_search(ctx.obj['accountId'], ctx.obj['aerframeApplication']['apiKey'], channelURL,
                                           num, None, ctx.obj['verbose'])


@aerframe.group()
@click.pass_context
def network(ctx):
    """AerFrame network commands
    \f

    """
    aerisutils.vprint(ctx, 'AerFrame network commands')


@network.command()  # Subcommand: aerframe network location
@click.pass_context
def location(ctx):
    """Get device network location from visited network
    \f

    """
    loc_info = aerframesdk.get_location(ctx.obj['accountId'], ctx.obj['aerframeApplication']['apiKey'], 'imsi',
                                        '204043398999957', ctx.obj['verbose'])
    print('Location information:\n' + json.dumps(loc_info, indent=4))


def main():
    mycli(obj={})


if __name__ == "__main__":
    mycli(obj={})
