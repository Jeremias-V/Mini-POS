# Mini-POS
A feature limited Point Of Sale (POS) web based system.

## Setup Project
1. Create a python virtual environment using `virtualenv .` inside the project parent directory.
2. Activate the venv using `source bin/activate`.
3. Install the required packages using `pip install -r requirements.txt`.
4. Create a database file using `touch mini-pos.db`.
5. Run `reset-db.sh` to setup the database (this script can also be run if you want to reset the database to its initial state).
6. Create a `.env` file inside the project parent directory and add two lines:
   1. One line should be `SECRET_KEY='<YOUR_SECRET_KEY>'`, <YOUR_SECRET_KEY> could be replaced with the result of running this command `python -c 'import secrets; print(secrets.token_hex())'`.
   2. The other line should be `DB_PATH='<YOUR_DATABASE_PATH>'`, <YOUR_DATABASE_PATH> should be replaced with the full path of your database location, if you follow this tutorial just copy the result of running `pwd` appending `/mini-pos.db` (while on project parent directory).

## Run project
1. Activate the venv using `source bin/activate` (if not previously activated).
2. Run `flask run` or `flask --debug run` if you want debugging mode.
