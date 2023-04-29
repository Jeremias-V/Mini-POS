FROM python:3.9-slim-buster

WORKDIR /api

COPY . .

RUN apt update && apt upgrade -y
RUN apt install -y sqlite3 virtualenv

RUN bash scripts/setup.sh

CMD ["bash", "scripts/docker-run.sh"]
