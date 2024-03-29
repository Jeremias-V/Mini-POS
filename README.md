# Mini-POS
A feature limited Point Of Sale (POS) API.

## Setup project
1. Install `Python 3.9`, `sqlite3` and `virtualenv`.
2. While on parent directory `Mini-POS/` run `bash scripts/setup.sh`

## Run project
1. Run `bash scripts/run.sh` from project parent directory.

## Alternative
You can also setup and run this flask api using a docker container, just run the following commands while on parent directory:
1. `sudo docker build --tag python-docker .`
2. `sudo docker run -d -p 5000:5000 python-docker`

To access the container you can use this command:

`sudo docker exec -it $(sudo docker ps | grep python-docker | awk '{print $1}') bash`

To stop the container you can use this command:

`sudo docker stop $(sudo docker ps | grep python-docker | awk '{print $1}')`

To delete the image you can use this command:

`sudo docker image rm -f $(sudo docker images | grep python-docker | awk '{print $3}')`

## Run Tests

- Run `bash scripts/test.sh` from project parent directory to run the unit tests.
- Run `bash scripts/coverage.sh` to get the tests coverage, if you want an interactive report with the lines that were executed, run `coverage html`.


