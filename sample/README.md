# Running the Sample Code

This sample project demonstrates the usage of the Aeris SDK for Connectivity APIs.

It should run "out of the box" by using the aerisapisdk modules that are part of this git repository...

```
$ cd sample
$ python3 aerframe_budget_geofence.py --help
```

...but, if you wish to install the aerisapisdk through pip, consider using a [virtual environment](https://docs.python.org/3/tutorial/venv.html):

```
$ cd sample
$ python3 -m venv venv
$ source venv/bin/activate
$ pip3 install aerisapisdk
$ python3 aerframe_budget_geofence.py --help
```

(Note: Windows users can run the `activate.bat` or `Activate.ps1` script instead of the `source` command. Those scripts are found inside `venv\Scripts\`)

When you are done, you can deactivate the virtual environment by running the `deactivate` command.
