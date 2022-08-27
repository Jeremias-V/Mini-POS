#!/bin/bash

if [ ! -f "mini-pos.db" ]; then
    echo "Couldn't find your database file named mini-pos.db"
    exit 1
fi

echo -n "Are you sure you want to reset your database? (y/n) "
read ans

if [ "$ans" != "y" ]; then
    echo "Your database was not modified"
    exit 1
fi

echo "Deleting your database and creating a new one..."

rm mini-pos.db

sqlite3 mini-pos.db ".databases"

source bin/activate

python3 -c 'from models import db; from app import app; db.init_app(app); db.create_all(app=app)'

echo "New database created!"

exit 0
