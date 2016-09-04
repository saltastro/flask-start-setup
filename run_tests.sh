#!/bin/bash

ERROR=0

python -m unittest discover tests/unittests
if [[ $? != 0 ]]
then
    ERROR=1
    echo 'Unit tests did NOT pass!' >&2
fi

python -m behave tests/features
if [[ $? != 0 ]]
then
    ERROR=1
    echo 'Behave tests did NOT pass!' >&2
fi

python -m pycodestyle --ignore=E402 --max-line-length=120 app tests
if [[ $? != 0 ]]
then
    ERROR=1
    echo 'PEP8 tests did NOT pass!' >&2
fi

exit $ERROR
