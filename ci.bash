#!/bin/bash
set -eo pipefail

function lint () {
    echo "Checking the code syntax"
    pycodestyle --first chaoslib
}

function build () {
    echo "Building the choastoolkit package"
    python3 setup.py build
}

function run-test () {
    echo "Running the tests"
    python3 setup.py test
}

function release () {
    echo "Releasing the package"
    python3 setup.py release

    echo "Publishing to PyPI"
    pip3 install twine
    twine upload dist/* -u ${PYPI_USER_NAME} -p ${PYPI_PWD}
}

function main () {
    lint || return 1
    build || return 1
    run-test || return 1

    if [[ "$TRAVIS_OS_NAME" == "linux" ]]; then
        if [[ $TRAVIS_PYTHON_VERSION =~ ^3\.5+$ ]]; then
            if [[ $TRAVIS_TAG =~ ^[0-9]+\.[0-9]+\.[0-9]+(rc[0-9]+)?$ ]]; then
                echo "Releasing tag $TRAVIS_TAG with Python $TRAVIS_PYTHON_VERSION"
                release || return 1
            fi
        fi
    fi
}

main "$@" || exit 1
exit 0
