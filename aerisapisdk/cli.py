import click
import json
import pathlib
import aerisapisdk.aeradminsdk as aeradminsdk
import aerisapisdk.aertrafficsdk as aertrafficsdk
import aerisapisdk.aerframesdk as aerframesdk
import aerisapisdk.aerisutils as aerisutils

# Resolve this user's home directory path
home_directory = str(pathlib.Path.home())
default_config_filename = home_directory + "/.aeris_config"
afsdkappname = 'aerframesdk'  # Short name used for the AerFrame application created for this SDK


# Loads configuration from file
def load_config(ctx, config_filename):
    try:
        with open(config_filename) as my_config_file:
            ctx.obj.update(json.load(my_config_file))
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
        json.dump(config_values, myconfigfile, indent=4)


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
    aeradminsdk.get_device_details(ctx.obj['verbose'], ctx.obj['accountId'], ctx.obj['apiKey'],
                                   ctx.obj['email'], ctx.obj['primaryDeviceIdType'], ctx.obj['primaryDeviceId'])


@aeradmin.command()  # Subcommand: aeradmin network
@click.pass_context
def network(ctx):
    """AerAdmin get device network details
    \f

    """
    aeradminsdk.get_device_network_details(ctx.obj['verbose'], ctx.obj['accountId'], ctx.obj['apiKey'],
                                           ctx.obj['email'], ctx.obj['primaryDeviceIdType'], ctx.obj['primaryDeviceId'])


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
    aertrafficsdk.get_device_summary_report(ctx.obj['accountId'], ctx.obj['apiKey'],
                                            ctx.obj['email'], ctx.obj['primaryDeviceIdType'],
                                            ctx.obj['primaryDeviceId'])


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
    aerframeApplicationId = aerframesdk.get_applications(ctx.obj['verbose'], ctx.obj['accountId'],
                                                         ctx.obj['apiKey'], afsdkappname)
    if aerframeApplicationId is None:
        aerframeApplication = aerframesdk.create_application(ctx.obj['verbose'], ctx.obj['accountId'],
                                                             ctx.obj['apiKey'], afsdkappname)
    else:
        aerframeApplication = aerframesdk.get_application(ctx.obj['verbose'], ctx.obj['accountId'],
                                                          ctx.obj['apiKey'], aerframeApplicationId)
    ctx.obj['aerframeApplication'] = aerframeApplication
    # Notification channel
    aerframeChannelId = aerframesdk.get_channels(ctx.obj['verbose'], ctx.obj['accountId'],
                                                 ctx.obj['apiKey'], afsdkappname)
    if aerframeChannelId is None:
        aerframeChannel = aerframesdk.create_channel(ctx.obj['verbose'], ctx.obj['accountId'],
                                                     ctx.obj['apiKey'], afsdkappname)
    else:
        aerframeChannel = aerframesdk.get_channel(ctx.obj['verbose'], ctx.obj['accountId'],
                                                  ctx.obj['apiKey'], aerframeChannelId)
    ctx.obj['aerframeChannel'] = aerframeChannel
    # Subscription
    appApiKey = ctx.obj['aerframeApplication']['apiKey']
    aerframeSubscriptionId = aerframesdk.get_outbound_subscriptions(ctx.obj['verbose'],
                                                                    ctx.obj['accountId'], appApiKey, afsdkappname)
    if aerframeSubscriptionId is None:
        afchid = ctx.obj['aerframeChannel']['resourceURL'].split('/channels/', 1)[1]
        aerframeSubscription = aerframesdk.create_outbound_subscription(ctx.obj['verbose'], ctx.obj['accountId'],
                                                                        appApiKey, afsdkappname, afchid)
    else:
        aerframeSubscription = aerframesdk.get_outbound_subscription(ctx.obj['verbose'], ctx.obj['accountId'],
                                                                     appApiKey, afsdkappname, aerframeSubscriptionId)
    ctx.obj['aerframeSubscription'] = aerframeSubscription
    aerisutils.vprint(ctx.obj['verbose'], '\nUpdated aerframe subscription config: ' + str(ctx.obj))
    # Device IDs
    deviceDetails = aeradminsdk.get_device_details(ctx.obj['verbose'], ctx.obj['accountId'], ctx.obj['apiKey'],
                                                   ctx.obj['email'], ctx.obj['primaryDeviceIdType'],
                                                   ctx.obj['primaryDeviceId'])
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
    aerframeSubscriptionId = aerframesdk.get_outbound_subscriptions(ctx.obj['verbose'],
                                                                    ctx.obj['accountId'], appApiKey, afsdkappname)
    if aerframeSubscriptionId is not None:
        aerframesdk.delete_outbound_subscription(ctx.obj['verbose'], ctx.obj['accountId'],
                                                 ctx.obj['aerframeApplication']['apiKey'], afsdkappname,
                                                 aerframeSubscriptionId)
        # Notification channel
    aerframeChannelId = aerframesdk.get_channels(ctx.obj['verbose'], ctx.obj['accountId'],
                                                 ctx.obj['apiKey'], afsdkappname)
    if aerframeChannelId is not None:
        aerframesdk.delete_channel(ctx.obj['verbose'], ctx.obj['accountId'], ctx.obj['apiKey'], aerframeChannelId)
        # AerFrame application
    aerframeApplicationId = aerframesdk.get_applications(ctx.obj['verbose'], ctx.obj['accountId'],
                                                         ctx.obj['apiKey'], afsdkappname)
    if aerframeApplicationId is not None:
        aerframesdk.delete_application(ctx.obj['verbose'], ctx.obj['accountId'], ctx.obj['apiKey'],
                                       aerframeApplicationId)


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
    afappid = aerframesdk.get_applications(ctx.obj['verbose'], ctx.obj['accountId'], ctx.obj['apiKey'], aps)
    if afappid != '':
        afappconfig = aerframesdk.get_application(ctx.obj['verbose'], ctx.obj['accountId'], ctx.obj['apiKey'], afappid)
        print('\nApp config: \n' + str(afappconfig))


@application.command()  # Subcommand: aerframe application create
@click.option('--aps', default=afsdkappname, help="Application short name to create")
@click.pass_context
def create(ctx, aps):
    """Create a new AerFrame application
    \f

    """
    aerframesdk.create_application(ctx.obj['verbose'], ctx.obj['accountId'], ctx.obj['apiKey'], aps)


@application.command()  # Subcommand: aerframe application delete
@click.option('--aps', default=afsdkappname, help="Application short name to delete")
@click.pass_context
def delete(ctx, aps):
    """Delete an AerFrame application
    \f

    """
    afappid = aerframesdk.get_applications(ctx.obj['verbose'], ctx.obj['accountId'], ctx.obj['apiKey'], aps)
    if afappid != '':
        click.confirm('Do you want to delete the app ' + aps + '?', abort=True)
        aerframesdk.delete_application(ctx.obj['verbose'], ctx.obj['accountId'], ctx.obj['apiKey'], afappid)


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
    appChannelID = aerframesdk.get_channels(ctx.obj['verbose'], ctx.obj['accountId'], ctx.obj['apiKey'], afsdkappname)
    aerframesdk.get_channel(ctx.obj['verbose'], ctx.obj['accountId'], ctx.obj['apiKey'], appChannelID)


@channel.command()  # Subcommand: aerframe create_channel
@click.pass_context
def create(ctx):
    """Create AerFrame notification channel
    \f

    """
    aerframesdk.create_channel(ctx.obj['verbose'], ctx.obj['accountId'], ctx.obj['apiKey'], 'aerframesdk')


@channel.command()  # Subcommand: aerframe channel delete
@click.pass_context
def delete(ctx):
    """Delete AerFrame notification channel
    \f

    """
    afchannelid = aerframesdk.get_channels(ctx.obj['verbose'], ctx.obj['accountId'], ctx.obj['apiKey'], afsdkappname)
    if afchannelid != '':
        click.confirm('Do you want to delete the sdk channel?', abort=True)
        aerframesdk.delete_channel(ctx.obj['verbose'], ctx.obj['accountId'], ctx.obj['apiKey'], afchannelid)


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
    aerframesdk.get_subscriptions(ctx.obj['verbose'], ctx.obj['accountId'],
                                  ctx.obj['aerframeApplication']['apiKey'], afsdkappname)


@subscription.command()  # Subcommand: aerframe subscription create
@click.pass_context
def create(ctx):
    """Create AerFrame subscription
    \f

    """
    appChannelID = aerframesdk.get_channels(ctx.obj['verbose'], ctx.obj['accountId'], ctx.obj['apiKey'], afsdkappname)
    aerframesdk.create_outbound_subscription(ctx.obj['verbose'], ctx.obj['accountId'],
                                             ctx.obj['aerframeApplication']['apiKey'], afsdkappname, appChannelID)


@subscription.command()  # Subcommand: aerframe subscription delete
@click.pass_context
def delete(ctx):
    """Delete AerFrame subscription
    \f

    """
    afsubid = aerframesdk.get_outbound_subscriptions(ctx.obj['verbose'], ctx.obj['accountId'],
                                                     ctx.obj['aerframeApplication']['apiKey'], afsdkappname)
    if afsubid != '':
        click.confirm('Do you want to delete the sdk subscription?', abort=True)
        aerframesdk.delete_outbound_subscription(ctx.obj['verbose'], ctx.obj['accountId'],
                                                 ctx.obj['aerframeApplication']['apiKey'], afsdkappname, afsubid)


@aerframe.group()
@click.pass_context
def sms(ctx):
    """AerFrame SMS commands
    \f

    """
    aerisutils.vprint(ctx, 'AerFrame sms commands')


@sms.command()  # Subcommand: aerframe sms send
@click.pass_context
def send(ctx):
    """Send an SMS
    \f

    """
    aerframesdk.send_mt_sms(ctx.obj['verbose'], ctx.obj['accountId'], ctx.obj['aerframeApplication']['apiKey'],
                            afsdkappname, ctx.obj['deviceId']['imsi'], 'Test from aerframesdk.')


@sms.command()  # Subcommand: aerframe sms send
@click.option('--num', default=1, help="Number of receive requests")
@click.pass_context
def receive(ctx, num):
    """Receive SMS or Delivery Receipt
    \f

    """
    channelURL = ctx.obj['aerframeChannel']['channelData']['channelURL']
    aerframesdk.notifications_flush_search(ctx.obj['verbose'], ctx.obj['accountId'],
                                           ctx.obj['aerframeApplication']['apiKey'],
                                           channelURL, num, None)


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
    aerframesdk.get_location(ctx.obj['verbose'], ctx.obj['accountId'],
                             ctx.obj['aerframeApplication']['apiKey'], 'imsi', '204043398999957')


def main():
    mycli(obj={})


if __name__ == "__main__":
    mycli(obj={})
