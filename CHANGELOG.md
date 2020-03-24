# Release: 0.1.5

(in progress)

Tags: n/a

Security notes:
* Version 0.1.4 and earlier did not set restrictive permissions on the configuration file created by the `aeriscli config` command; this could allow other users on your system to read the contents of that file. Version 0.1.5 attempts to restrict the permissions of that file when running the `aeriscli config`. Users upgrading from 0.1.4 or earlier are encouraged to either run `aeriscli config` again or set the permissions of the configuration file appropriately.

New features or changes:
* updates methods to raise an exception if the HTTP status code indicates a failure
* updates the names of some methods to more closely align with their function
    * example: `get_outbound_subscription` to `get_outbound_subscription_id_by_app_short_name`
* adds CONTRIBUTING.md

Bug fixes:
* miscellaneous typos

# Release: 0.1.4

Tags: n/a

New features:
* initial release

Bug fixes:
* n/a
