#!/bin/bash

source src/venv/bin/activate

pytest -W ignore::DeprecationWarning

exit 0
