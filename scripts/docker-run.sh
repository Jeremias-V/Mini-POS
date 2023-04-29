#!/bin/bash

source src/venv/bin/activate
(cd src; flask run --host=0.0.0.0 --port=5000)

exit 0
