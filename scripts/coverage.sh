#!/bin/bash

source src/venv/bin/activate

coverage run -m pytest -W ignore::DeprecationWarning
coverage report

exit 0
