# Mini-POS
A feature limited Point Of Sale (POS) web based system.

## Setup project
1. Install `Python 3.9`, `sqlite3` and `virtualenv`.
2. While on parent directory `Mini-POS/` run `bash scripts/setup.sh`

## Run project
1. Run `bash scripts/run.sh` from project parent directory.

## Alternative
You can also setup and run this flask api using a docker container, just run the following commands while on parent directory:
1. `sudo docker build --tag python-docker .`.
2. `sudo docker run -p 5000:5000 python-docker`.

If you want to stop the container you can use this command:
`sudo docker stop $(sudo docker ps | grep python-docker | awk '{print $1}')`

If you want to delete the image use this command:
`sudo docker image rm -f $(sudo docker images | grep python-docker | awk '{print $3}')`
