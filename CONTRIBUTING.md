# Contributing to aeris-apisdk-py

⚠ **Important!** ⚠

Do not provide API keys via GitHub, whether through issues, contributed code, or documentation.

## Submitting Issues

### Security Issues

Please see our security policy. If our security policy is missing, and you like creating excellent security policies, why not [help us out](https://www.aeris.com/careers/)?

### Issues with Aeris APIs or Services

If you believe you have found an issue with Aeris APIs or services, please submit a service request through https://aeriscom.zendesk.com/hc/en-us/requests/new

### Issues with aeris-apisdk-py

If you wish to report a bug report or enhancement, please ensure it was not already reported by searching under Issues.

Please include the following information with your bug reports:

* Python version
* operating system version
* version of the aeris-apisdk-py installed (e.g., from `pip3 list`)
* pip version (e.g., `pip3 --version`) or poetry version (e.g., `poetry --version`), as appropriate
* steps to reproduce

If you need to provide the configuration file created by the `aeriscli config` command, **please** redact your API key(s), and consider redacting your account ID, email, and any device identifiers.


## Submitting Pull Requests

Before submitting a pull request, please be sure it passes our [functional tests](https://github.com/aeristhings/aeris-apisdk-py#functional-tests) and [coding style tests](https://github.com/aeristhings/aeris-apisdk-py#coding-style-tests).

The following is only relevant if the major version of aeris-apisdk-py is greater than zero (0):

If your changes would break backwards compatibility, please:

* mention this in your pull request,
* run `poetry version major` as part of your changes, or
* both of the above.
