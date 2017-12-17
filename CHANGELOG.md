# Changelog

## [Unreleased][]

[Unreleased]: https://github.com/chaostoolkit/chaostoolkit-lib/compare/0.8.0...HEAD

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