#!/bin/bash

source src/venv/bin/activate
flask --app src/ run --host=0.0.0.0 --port=5000

exit 0
