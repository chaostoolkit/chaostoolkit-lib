# chaostoolkit-lib

[![Build Status](https://travis-ci.org/chaostoolkit/chaostoolkit-lib.svg?branch=master)](https://travis-ci.org/chaostoolkit/chaostoolkit-lib)
[![Python versions](https://img.shields.io/pypi/pyversions/chaostoolkit-lib.svg)](https://www.python.org/)
[![Requirements Status](https://requires.io/github/chaostoolkit/chaostoolkit-lib/requirements.svg?branch=master)](https://requires.io/github/chaostoolkit/chaostoolkit-lib/requirements/?branch=master)

The Chaos Toolkit core library.

## Purpose

The purpose of this library is to provide the core of the Chaos Toolkit 
[model][concepts] and functions it needs to render its services.

Unless you wish to create your own toolkit, you will likely not use directly
this library.

[concepts]: http://chaostoolkit.org/overview/concepts/

## Features

The library provides the followings features:

* discover capabilities from extensions
  Allows you to explore the support from an extension that would help you
  initialize an experiment against the system this extension targets

* validate a given experiment syntax
  The validation looks at various keys in the experiment and raises errors
  whenever something doesn't look right.
  As a nice addition, when a probe calls a Python function with arguments,
  it tries to validate the given argument list matches the signature of the
  function to apply.

* run your steady state before and after the method. The former as a gate to
  decide if the experiment can be executed. The latter to see if the system
  deviated from normal.

* run probes and actions declared in an experiment
  It runs the steps in a experiment method sequentially, applying first steady
  probes, then actions and finally close probes.

  A journal, as a JSON payload, is return of the experiment run.

  The library supports running probes and actions defined as Python functions,
  from importable Python modules, processes and HTTP calls.

* run experiment's rollbacks when provided

* Load secrets from the experiments, the environ or [vault][vault]

* Provides event notification from Chaos Toolkit flow (although the actual
  events are published by the CLI itself, not from this library), supported
  events are:
  * on experiment validation: started, failed or completed
  * on discovery: started, failed or completed
  * on initialization of experiments: started, failed or completed
  * on experiment runs: started, failed or completed

  For each event, the according payload is part of the event as well as a UTC
  timestamp.

[vault]: https://www.vaultproject.io/

## Install

If you are user of the Chaos Toolkit, you probably do not need to install this
package yourself as it comes along with the [chaostoolkit cli][cli].

[cli]: https://github.com/chaostoolkit/chaostoolkit

However, should you wish to integrate this library in your own Python code,
please install it as usual:

```
$ pip install -U chaostoolkit-lib
```

### Specific dependencies

In addition to essential dependencies, the package can install a couple of
other extra dependencies for specific use-cases. They are not mandatory and
the library will warn you if you try to use a feature that requires them.

If you need [Vault][vault] support to read secrets from, run the following
command:

[vault]: https://www.vaultproject.io/
```
$ pip install -U chaostoolkit-lib[vault]
```

If you need [JSON Path support][jpath] for tolerance probes in the hypothesis,
also run the following command:

[jpath]: http://goessner.net/articles/JsonPath/

```
$ pip install -U chaostoolkit-lib[jsonpath]
```

## Contribute

Contributors to this project are welcome as this is an open-source effort that
seeks [discussions][join] and continuous improvement.

[join]: https://join.chaostoolkit.org/

From a code perspective, if you wish to contribute, you will need to run a 
Python 3.5+ environment. Then, fork this repository and submit a PR. The
project cares for code readability and checks the code style to match best
practices defined in [PEP8][pep8]. Please also make sure you provide tests
whenever you submit a PR so we keep the code reliable.

[pep8]: https://pycodestyle.readthedocs.io/en/latest/

The Chaos Toolkit projects require all contributors must sign a
[Developer Certificate of Origin][dco] on each commit they would like to merge
into the master branch of the repository. Please, make sure you can abide by
the rules of the DCO before submitting a PR.

[dco]: https://github.com/probot/dco#how-it-works