# Changelog

## [Unreleased][]

[Unreleased]: https://github.com/chaostoolkit/chaostoolkit-lib/compare/0.14.0...HEAD

## [0.14.0][] - 2018-02-06

[0.14.0]: https://github.com/chaostoolkit/chaostoolkit-lib/compare/0.13.1...0.14.0

### Changed

-   Do not fail the discovery when an extension is missing the `__all__`
    attribute [#28][28]
-   Include extension activity arguments type when discovering
    extension [#19][19]

[19]: https://github.com/chaostoolkit/chaostoolkit-lib/issues/19
[28]: https://github.com/chaostoolkit/chaostoolkit-lib/issues/28

## [0.13.1][] - 2018-01-30

[0.13.1]: https://github.com/chaostoolkit/chaostoolkit-lib/compare/0.13.0...0.13.1

### Changed

-   Steady stade is optional, so don't expect it here

## [0.13.0][] - 2018-01-28

[0.13.0]: https://github.com/chaostoolkit/chaostoolkit-lib/compare/0.12.2...0.13.0

### Changed

-   HTTP provider must be able to connect to self-signed HTTPS endpoint [#25][25]
-   Steady state is now added to the generated json report

[25]: https://github.com/chaostoolkit/chaostoolkit-lib/issues/25

## [0.12.2][] - 2018-01-24

[0.12.2]: https://github.com/chaostoolkit/chaostoolkit-lib/compare/0.12.1...0.12.2

### Changed

-   missing hvac dependency should not break chaos with an exception [#23][23]

[23]: https://github.com/chaostoolkit/chaostoolkit-lib/issues/23

## [0.12.1][] - 2018-01-20

[0.12.1]: https://github.com/chaostoolkit/chaostoolkit-lib/compare/0.12.0...0.12.1

### Changed

-   yaml is not required in this package

## [0.12.0][] - 2018-01-20

[0.12.0]: https://github.com/chaostoolkit/chaostoolkit-lib/compare/0.11.0...0.12.0

### Changed

- Various dependencies cleanups
- Added the DCO notice for contributors

## [0.11.0][] - 2018-01-17

[0.11.0]: https://github.com/chaostoolkit/chaostoolkit-lib/compare/0.10.0...0.11.0

### Changed

- Steady state hypothesis is not mandatory when exploring [#18][18]

[18]: https://github.com/chaostoolkit/chaostoolkit/issues/18

## [0.10.0][] - 2018-01-16

[0.10.0]: https://github.com/chaostoolkit/chaostoolkit-lib/compare/0.9.4...0.10.0

### Added

- New discovery of extension capabilities [#16][16]

### Changed

- Pinning ply dependency version to 3.4 to avoid random install failures [#8][8]

[8]: https://github.com/chaostoolkit/chaostoolkit-lib/issues/8
[16]: https://github.com/chaostoolkit/chaostoolkit-lib/issues/16

## [0.9.4][] - 2018-01-10

[0.9.4]: https://github.com/chaostoolkit/chaostoolkit-lib/compare/0.9.3...0.9.4

### Changed

- Proper merge of secrets from the different supported loaders

## [0.9.3][] - 2018-01-09

[0.9.3]: https://github.com/chaostoolkit/chaostoolkit-lib/compare/0.9.2...0.9.3

### Changed

- Do not forget to load inlined secrets

## [0.9.2][] - 2018-01-05

[0.9.2]: https://github.com/chaostoolkit/chaostoolkit-lib/compare/0.9.1...0.9.2

### Changed

- HTTP probe header dict must be serialiable back to JSON

## [0.9.1][] - 2018-01-05

[0.9.1]: https://github.com/chaostoolkit/chaostoolkit-lib/compare/0.9.0...0.9.1

### Removed

- HTTP activity will not check status code any longer [#10][10]
- Process activity will not check return code any longer [#10][10]

[10]: https://github.com/chaostoolkit/chaostoolkit-lib/issues/10

## [0.9.0][] - 2018-01-05

[0.9.0]: https://github.com/chaostoolkit/chaostoolkit-lib/compare/0.8.2...0.9.0

### Added

- Steady state is now run after the method as well [#19][19]
- Allow tolerance to be based on the HTTP status code of the probe [#20][20]

### Changed

- Logging when an activity runs in the background
- Pause after we capture the end time of an activity
- HTTP Probe now returns a dict with status code, headers and body of the
  response

[19]: https://github.com/chaostoolkit/chaostoolkit/issues/19
[20]: https://github.com/chaostoolkit/chaostoolkit/issues/20

## [0.8.2][] - 2017-12-18

[0.8.2]: https://github.com/chaostoolkit/chaostoolkit-lib/compare/0.8.1...0.8.2

### Changed

- Missing transitive dependency "ply"

## [0.8.1][] - 2017-12-18

[0.8.1]: https://github.com/chaostoolkit/chaostoolkit-lib/compare/0.8.0...0.8.1

### Changed

- Packaging up the dev requirements for install from the tarball

## [0.8.0][] - 2017-12-17

[0.8.0]: https://github.com/chaostoolkit/chaostoolkit-lib/compare/0.7.0...0.8.0

### Added

- Substitution from configuration and secrets so values can be dynamically set
- The journal contains now a global status of the run

### Changed

- Pausing activity message is logged before the activity running message for
  better clarity
- Arguments are now substituted with their configuration and secrets values
  before being applied

## [0.7.0][] - 2017-12-12

[0.7.0]: https://github.com/chaostoolkit/chaostoolkit-lib/compare/0.6.0...0.7.0

### Added

- Configuration schema support
- Lots of logging added at the DEBUG level
- [EXPERIMENTAL] Loading secrets froom HashiCorp vault

### Changed

- [BREAKING] Secrets from environment variable now respects the API and do not
  get detected by parsing the secret's value
- Better handling of the steady hypothesis not matching its expectations
  Now the experiment terminates cleanly

## [0.6.0][] - 2017-12-06

[0.6.0]: https://github.com/chaostoolkit/chaostoolkit-lib/compare/0.5.1...0.6.0

### Changed

* [BREAKING]: The specification has changed in a non-compatible way. We are
  working towards a 1.0.0 version of the specification as the initial draft was
  merely to set the stage. The `method` has been simplified and there are no
  more `steady` and `close` probes, only probes. We also now define a steady
  state hypothesis that would fail the experiment should it not meet its
  expected state. Finally, we define a `rollbacks` entry so that experiments
  can revert changes they made

### Added

* Experiment captures now SIGINT and system exit signals and swallows them so
  the journal is returned and can be inspected
* Activities can be cached and referenced from within experiment


## [0.5.1][] - 2017-11-23

[0.5.1]: https://github.com/chaostoolkit/chaostoolkit-lib/compare/0.5.0...0.5.1

### Changed

-   Do not shadow functions
-   Log full errors on debug level
-   Always pause even if activity failed


## [0.5.0][] - 2017-11-19

[0.5.0]: https://github.com/chaostoolkit/chaostoolkit-lib/compare/0.4.0...0.5.0

### Changed

-   Split the inner of `run_experiment` into various functions for better
    composability
-   Pause before/after activity


## [0.4.0][] - 2017-10-18

[0.4.0]: https://github.com/chaostoolkit/chaostoolkit-lib/compare/0.3.0...0.4.0

### Changed

-   Better logging

## [0.3.0][] - 2017-10-18

[0.3.0]: https://github.com/chaostoolkit/chaostoolkit-lib/compare/0.2.0...0.3.0

### Added

-   An `expected_status` for HTTP probe to consider HTTP errors as expected in
    some cases

## [0.2.0][] - 2017-10-10

[0.2.0]: https://github.com/chaostoolkit/chaostoolkit-lib/compare/0.1.1...0.2.0

### Added

-   A first draft to loading secrets from environment
-   Passing those secrets as a mapping to actions and probes expecting them
-   Added support for background activities
-   Dry mode support

### Removed

-   Unused layer module

## [0.1.1][] - 2017-10-06

[0.1.1]: https://github.com/chaostoolkit/chaostoolkit-lib/compare/0.1.0...0.1.1

### Changed

-   Package up extra files when installed from source

## [0.1.0][] - 2017-10-06

[0.1.0]: https://github.com/chaostoolkit/chaostoolkit-lib/tree/0.1.0

### Added

-   Initial release