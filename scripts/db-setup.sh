#!/bin/bash

if [ -d "instance/" ]; then
    echo "The database directory already exists."
    exit 1
fi

mkdir instance

exit 0
