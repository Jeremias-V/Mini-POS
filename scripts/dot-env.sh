#!/bin/bash

if [ -f ".env" ]; then
    echo "The .env file already exists, skipping the script."
    exit 1
fi

touch .env

# SECRET KEY
echo -n "SECRET_KEY='" >> .env
echo -n "$(python -c 'import secrets; print(secrets.token_hex())')" >> .env
echo "'" >> .env

# DB PATH
echo -n "DB_PATH='" >> .env
echo -n "$(pwd)/instance/mini-pos.db" >> .env
echo "'" >> .env

# ADMIN REGISTER KEY
echo -n "ADMIN_KEY='" >> .env
echo -n "$(python -c 'import secrets; print(secrets.token_hex()[:8])')" >> .env
echo "'" >> .env

echo "The .env file has been successfully created!"

exit 0
