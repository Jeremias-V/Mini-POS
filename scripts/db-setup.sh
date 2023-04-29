#!/bin/bash

if [ -f "instance/mini-pos.db" ]; then
    echo "The database file already exists."
    exit 1
fi

mkdir instance
touch instance/mini-pos.db
bash scripts/db-reset.sh -y

exit 0