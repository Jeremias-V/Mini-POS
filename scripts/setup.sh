#!/bin/bash

if [ -f "scripts/.setup-done" ]; then
    echo "The project was already setup."
    exit 1
fi

virtualenv --python="$(which python3.9)" ./src
if [ $? -eq 0 ]; then
    echo -e "\nSuccessfully created the python virtual environment.\n"
else
    echo -e "\nAn error ocurred while creating the python virtual environment.\n"
    exit 1
fi

source src/bin/activate
if [ $? -eq 0 ]; then
    echo -e "\nPython virtual environment activated!\n"
else
    echo -e "\nAn error ocurred while activating the python virtual environment.\n"
    exit 1
fi

pip install -r requirements.txt
if [ $? -eq 0 ]; then
    echo -e "\nSuccessfully installed the requirements.txt\n"
else
    echo -e "\nAn error ocurred while installing the requirements.txt\n"
    exit 1
fi


bash scripts/dot-env.sh
bash scripts/db-setup.sh

touch scripts/.setup-done
echo -e "\nThe project was setup successfully, try running it with 'bash scripts/run.sh'\n"
exit 0
