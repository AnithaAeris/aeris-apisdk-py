# aeris-apisdk-py
SDK and CLI for Aeris connectivity apis

## Getting Started - Deployment

OS environments tested so far: 
* Ubuntu 18 on Windows 10
* Windows 10 cmd shell

Python environments tested so far:
* Python 3.7.5 / pip 19.3.1

Installation / upgrade:
* 'pip install aerisapisdk'
* 'pip install --upgrade aerisapisdk'


Run:
~~~
'aeriscli' (Runs this way because aericli script gets installed in python/bin or python/scripts directory)
'python -m aerisapisdk.cli' (Run via module command)
~~~

## Getting Started - Development

These instructions will get you a copy of the project up and running on your local machine for development and testing purposes.

### Prerequisites

What you need to develop and test.

What I'm using:

```
git --version = 2.17.1
python --version = 3.7.5
pip --version = 19.3.1
poetry --version = 1.0.0
```

### Installing

A step by step series of examples that tell you how to get a development env running

Step 1: Clone the source to your local machine

```
>git clone https://github.com/aerisiot/aeris-apisdk-py.git

Cloning into 'aeris-apisdk-py'...
remote: Enumerating objects: 38, done.
remote: Counting objects: 100% (38/38), done.
remote: Compressing objects: 100% (36/36), done.
remote: Total 38 (delta 12), reused 14 (delta 0), pack-reused 0
Unpacking objects: 100% (38/38), done.
```

Step 2: Install dependencies

```
>cd aeris-apisdk-py
>poetry update

Updating dependencies
Resolving dependencies... (0.9s)

Writing lock file


Package operations: 18 installs, 0 updates, 0 removals

  - Installing more-itertools (8.1.0)
  - Installing zipp (1.0.0)
  - Installing importlib-metadata (1.4.0)
  - Installing pyparsing (2.4.6)
  - Installing six (1.13.0)
  - Installing attrs (19.3.0)
  - Installing certifi (2019.11.28)
  - Installing chardet (3.0.4)
  - Installing idna (2.8)
  - Installing packaging (20.0)
  - Installing pluggy (0.13.1)
  - Installing py (1.8.1)
  - Installing urllib3 (1.25.7)
  - Installing wcwidth (0.1.8)
  - Installing click (7.0)
  - Installing pathlib (1.0.1)
  - Installing pytest (5.3.2)
  - Installing requests (2.22.0)
```

Step 3: Verify development environment working

```
>poetry run aeriscli

Usage: aeriscli [OPTIONS] COMMAND [ARGS]...

Options:
  -v, --verbose             Verbose output
  -cfg, --config-file TEXT  Path to aservices config file.
  --help                    Show this message and exit.

Commands:
  aeradmin    AerAdmin API Services
  aerframe    AerFrame API Services
  aertraffic  AerTraffic API Services
  config      Set up the configuration for using this tool
```



## Running the tests

This section covers the automated tests for this system

### Functional tests

This project uses pytest for running functional tests

```
>poetry run pytest
================================================= test session starts ==================================================
platform linux -- Python 3.7.5, pytest-5.3.2, py-1.8.1, pluggy-0.13.1
rootdir: ~/aeris-apisdk-py
collected 1 item

tests/test_aerisapisdk.py .                                                                                      [100%]

================================================== 1 passed in 0.04s ===================================================
```

### Coding style tests

Explain what these tests test and why

```
Give an example
```


## Built With

* [Poetry](https://python-poetry.org/) - Python dependency management
* [Click](https://click.palletsprojects.com/en/7.x/) - Python package for creating beautiful command line interfaces

## Contributing

Please read [CONTRIBUTING.md] for details on our code of conduct, and the process for submitting pull requests to us.

## Versioning

We use [SemVer](http://semver.org/) for versioning. For the versions available, see the [tags on this repository](https://github.com/your/project/tags). 

## Authors

* **Drew Johnson** - *Initial work*

See also the list of [contributors](https://github.com/your/project/contributors) who participated in this project.

## License

This project is licensed under the Apache 2.0 License - see the [LICENSE.md](LICENSE.md) file for details

## Acknowledgments

* Hat tip to anyone whose code was used
