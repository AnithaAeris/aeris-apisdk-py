# Running the Sample Code

This sample project demonstrates the usage of the Aeris SDK for Connectivity APIs.

Before running, you should create a configuration file via the `aeriscli config` (or `poetry run aeriscli config`) command. 

This sample should run "out of the box" by using the aerisapisdk modules that are part of this git repository...

```
$ poetry run aeriscli config
...answer the prompts...
$ cd sample
$ python3 aerframe_budget_geofence.py --help
$ python3 aerframe_budget_geofence.py --config-file ~/.aeris_config --imsi 204041234567890
```

...but, if you wish to install the aerisapisdk through pip, consider using a [virtual environment](https://docs.python.org/3/tutorial/venv.html):

```
$ cd sample
$ python3 -m venv venv
$ source venv/bin/activate
$ pip3 install aerisapisdk
$ aeriscli config
...answer the prompts...
$ python3 aerframe_budget_geofence.py --help
$ python3 aerframe_budget_geofence.py --config-file ~/.aeris_config --imsi 204041234567890
```

(Note: Windows users can run the `activate.bat` or `Activate.ps1` script instead of the `source` command. Those scripts are found inside `venv\Scripts\`)

When you are done, you can deactivate the virtual environment by running the `deactivate` command.
