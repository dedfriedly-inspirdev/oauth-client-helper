# pull official base image
FROM python:3.7-slim-buster as base

# set environment varibles
ENV PYTHONDONTWRITEBYTECODE 1
ENV PYTHONUNBUFFERED 1

# set work directory
ARG CODEDIR=/usr/local/src
ENV CODEDIR=${CODEDIR}

# install psycopg2
RUN apt-get update && apt-get upgrade -y
RUN apt-get install -y make automake gcc g++ python3-dev netcat locales
RUN apt-get install -y libpq-dev libffi-dev

# set locale info
RUN echo 'en_US.UTF-8 UTF-8' >> /etc/locale.gen
RUN locale-gen
ENV LANG='en_US.UTF-8' LANGUAGE='en_US:en' LC_ALL='en_US.UTF-8'
RUN update-locale 

WORKDIR /tmp

# install dependencies
RUN pip install --no-cache-dir --upgrade pip
RUN pip install --no-cache-dir poetry
COPY ./poetry.lock .
COPY ./poetry.toml .
COPY ./pyproject.toml .
# PROD image
FROM base as prod_py
WORKDIR /tmp
RUN poetry install --no-root --no-dev
## DEV image
FROM base as dev_py
RUN apt-get install -y vim
WORKDIR /tmp
RUN pip install --no-cache-dir poetry
RUN poetry install --no-root
# Bulding prod 
FROM prod_py as prod
WORKDIR /
COPY docker/entrypoint.sh entrypoint.sh
RUN chmod +x /entrypoint.sh
WORKDIR ${CODEDIR}
COPY ./src .
ENTRYPOINT ["/entrypoint.sh"]
#Buliding dev
FROM dev_py as dev
WORKDIR /
COPY docker/entrypoint.sh entrypoint.sh
RUN chmod +x /entrypoint.sh
WORKDIR ${CODEDIR}
COPY ./src .
ENTRYPOINT ["/entrypoint.sh"]




