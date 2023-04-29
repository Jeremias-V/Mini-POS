#!/bin/bash

if [ ! -f "instance/mini-pos.db" ]; then
    echo "Couldn't find your database file named mini-pos.db"
    exit 1
fi

if [ "$1" != "-y" ]; then
    echo -n "Are you sure you want to reset your database? (y/n) "
    read ans
    if [ "$ans" != "y" ]; then
        echo "Your database was not modified"
        exit 1
    fi
    echo "Deleting your database and creating a new one..."
fi

rm instance/mini-pos.db

sqlite3 instance/mini-pos.db ".databases"

source src/bin/activate

(cd src/; python3 -c 'from models import db; from app import app; db.init_app(app); db.create_all(app=app)')

echo "New database file created!"

exit 0
