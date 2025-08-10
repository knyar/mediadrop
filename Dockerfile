FROM debian:buster-slim

RUN echo 'deb http://archive.debian.org/debian buster main contrib non-free' > /etc/apt/sources.list
RUN echo 'deb http://archive.debian.org/debian-security buster/updates main contrib non-free' >> /etc/apt/sources.list
RUN echo 'deb http://archive.debian.org/debian buster-backports main contrib non-free' >> /etc/apt/sources.list

RUN apt-get update -y && \
  apt-get install -y --no-install-recommends \
  build-essential \
  libmariadb-dev-compat \
  libmariadbclient-dev \
  libmariadb3 \
  python2.7-dev \
  python-virtualenv \
  virtualenv \
  libjpeg-dev \
  libfreetype6-dev \
  uwsgi \
  uwsgi-plugin-python

RUN apt-get autoremove -y

RUN groupadd --gid 1011 media \
    && useradd --uid 1011 --gid media --shell /bin/bash -d /app media

RUN mkdir -p /app/src && chown -R media:media /app

USER media
WORKDIR /app/src
ADD --chown=media:media . .

RUN virtualenv -p python2.7 --no-site-packages /app/venv
RUN /app/venv/bin/python2.7 setup.py develop

WORKDIR /app/deployment
CMD /usr/bin/uwsgi --plugin python --ini-paste deployment.ini
