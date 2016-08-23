#!/bin/bash

`python -m unittest discover tests/unittests`
if [[ $? = 0 ]]
then
    echo 'Unit tests passed!'
else
    echo 'Unit tests did NOT pass!'
fi
